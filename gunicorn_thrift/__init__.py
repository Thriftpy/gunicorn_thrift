__version__ = "0.0.1"

import gunicorn.workers

gunicorn.workers.SUPPORTED_WORKERS.update({
    'thrift_sync': 'gunicorn_thrift.sync_worker.SyncThriftWorker',
    })
