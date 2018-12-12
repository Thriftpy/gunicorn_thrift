# -*- coding: utf-8 -*-


import sys
import time
import errno
import socket
import logging
import traceback

try:
    import thread
except ImportError:
    # Python 3
    import _thread as thread

try:
    import gevent
    import gevent.monkey
    import greenlet
except RuntimeError:
    raise RuntimeError('`thriftpy_gevent` worker is unavailable because '
                       'gevent is not installed')

try:
    import thriftpy2
except ImportError:
    raise RuntimeError('`thriftpy_gevent` worker is unavailable because '
                       'thriftpy2 is not installed')


from thriftpy2.transport import TSocket
from thriftpy2.transport import TTransportException
from thriftpy2.protocol.exc import TProtocolException
from thriftpy2.protocol.cybin import ProtocolError
from thriftpy2.thrift import TDecodeException

from gunicorn.errors import AppImportError
from gunicorn.workers.ggevent import GeventWorker

from .utils import ProcessorMixin

logger = logging.getLogger(__name__)


# Take references to un-monkey-patched versions of stuff we need.
# Monkey-patching will have already been done by the time we come to
# use these functions at runtime.
# And there's a change thread is already patched when importing this module,
# so we check first if it's already patched.
def __get_real_function(module, name):
    patched_origin = gevent.monkey.saved.get(module.__name__, {}).get(name)
    if not patched_origin:
        patched_origin = getattr(module, name)
    return patched_origin


_real_sleep = __get_real_function(time, 'sleep')
_real_start_new_thread = __get_real_function(thread, 'start_new_thread')
_real_get_ident = __get_real_function(thread, 'get_ident')


def check_protocol_and_transport(app):
    if not app.cfg.thrift_protocol_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use protocol from thriftpy,'
            'specify `thrift_protocol_factory` as one of the '
            'following:'
            '`thriftpy2.protocol:TCyBinaryProtocolFactory`, '
            '`thriftpy2.protocol:TBinaryProtocolFactory`'
            )

    if not app.cfg.thrift_transport_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use transport from thriftpy,'
            'specify `thrift_transport_factory` as one of the '
            'following:'
            '`thriftpy2.transport:TCyBufferedTransportFactory`, '
            '`thriftpy2.transport:TBufferedTransportFactory`'
            )


class GeventThriftPyWorker(GeventWorker, ProcessorMixin):
    def init_process(self):
        # Set up a greenlet tracing hook to monitor for event-loop blockage,
        # but only if monitoring is both possible and required.
        if hasattr(greenlet, "settrace") and \
                self.app.cfg.gevent_check_interval > 0:
            # Grab a reference to the gevent hub.
            # It is needed in a background thread, but is only visible from
            # the main thread, so we need to store an explicit reference to it.
            self._active_hub = gevent.hub.get_hub()
            # Set up a trace function to record each greenlet switch.
            self._active_greenlet = None
            self._greenlet_switch_counter = 0
            greenlet.settrace(self._greenlet_switch_tracer)
            self._main_thread_id = _real_get_ident()
            # Create a real thread to monitor out execution.
            # Since this will be a long-running daemon thread, it's OK to
            # fire-and-forget using the low-level start_new_thread function.
            _real_start_new_thread(self._process_monitoring_thread, ())

        return super(GeventThriftPyWorker, self).init_process()

    def _greenlet_switch_tracer(self, what, where):
        """Callback method executed on every greenlet switch.

        The worker arranges for this method to be called on every greenlet
        switch.  It keeps track of which greenlet is currently active and
        increments a counter to track how many switches have been performed.
        """
        # Increment the counter to indicate that a switch took place.
        # This will periodically be reset to zero by the monitoring thread,
        # so we don't need to worry about it growing without bound.
        origin, target = where
        self._active_greenlet = target
        self._greenlet_switch_counter += 1

    def _process_monitoring_thread(self):
        """Method run in background thread that monitors our execution.

        This method is an endless loop that gets executed in a background
        thread.  It periodically wakes up and checks:

            * whether the active greenlet has switched since last checked

        """
        try:
            while True:
                _real_sleep(self.app.cfg.gevent_check_interval)
                self._check_greenlet_blocking()
        except Exception:
            # Swallow any exceptions raised during interpreter shutdown.
            # Daemonic Thread objects have this same behaviour.
            if sys is not None:
                raise

    def _check_greenlet_blocking(self):
        # If there have been no greenlet switches since we last checked,
        # grab the stack trace and log an error.  The active greenlet's frame
        # is not available from the greenlet object itself, we have to look
        # up the current frame of the main thread for the traceback.
        if self._greenlet_switch_counter == 0:
            active_greenlet = self._active_greenlet
            # The hub gets a free pass, since it blocks waiting for IO.
            if active_greenlet not in (None, self._active_hub):
                frame = sys._current_frames()[self._main_thread_id]
                stack = traceback.format_stack(frame)
                err_log = ["Greenlet appears to be blocked\n"] + stack
                logger.error("".join(err_log))
        # Reset the count to zero.
        # This might race with it being incremented in the main thread,
        # but not often enough to cause a false positive.
        self._greenlet_switch_counter = 0

    def run(self):
        check_protocol_and_transport(self.app)
        super(GeventThriftPyWorker, self).run()

    def handle(self, listener, client, addr):
        self.cfg.on_connected(self, addr)
        if self.app.cfg.thrift_client_timeout is not None:
            client.settimeout(self.app.cfg.thrift_client_timeout)

        result = TSocket()
        result.set_handle(client)

        try:
            itrans = self.app.tfactory.get_transport(result)
            otrans = self.app.tfactory.get_transport(result)
            iprot = self.app.pfactory.get_protocol(itrans)
            oprot = self.app.pfactory.get_protocol(otrans)

            processor = self.get_thrift_processor()

            try:
                while True:
                    processor.process(iprot, oprot)
            except TTransportException:
                pass
        except (TProtocolException, ProtocolError) as err:
            self.log.warning(
                "Protocol error, is client(%s) correct? %s", addr, err
                )
        except TDecodeException as err:
            self.log.exception('%r: %r', addr, err)
            self.cfg.on_tdecode_exception(err)
        except socket.timeout:
            self.log.warning('Client timeout: %r', addr)
        except socket.error as e:
            if e.args[0] == errno.ECONNRESET:
                self.log.debug('%r: %r', addr, e)
            elif e.args[0] == errno.EPIPE:
                self.log.warning('%r: %r', addr, e)
            else:
                self.log.exception('%r: %r', addr, e)
        except Exception as e:
            self.log.exception('%r: %r', addr, e)
        finally:
            itrans.close()
            otrans.close()
            self.cfg.post_connect_closed(self)

    def handle_exit(self, sig, frame):
        ret = super(GeventThriftPyWorker, self).handle_exit(sig, frame)
        self.cfg.worker_term(self)
        return ret
