'''
Common logger library

[Config]
log_dir: log files directory. If specified as '@stdout', the log will output to `stderr`. Default './log'.
sentry_dsn: sentry dsn. default no sentry
rollover_when: rollover interval. default 'MIDNIGHT'
	S - Seconds
	M - Minutes
	H - Hours
	D - Days
	MIDNIGHT - roll over at midnight
rollover_backup_count: how many backup log files are kept. default 30
	if rollover_backup_count = 0, all log files are kept.
	if rollover_backup_count > 0, when rollover is done, no more than rollover_backup_count files are kept - the oldest ones are deleted.

[Normal Python Program]
# config.py
# Add LOGGER_CONFIG
LOGGER_CONFIG = {
	'log_dir': './log',
	'sentry_dsn': 'http://xxxxxxxx',
}
#if no config.py, will use './log' as log_dir

'''

log_data = None


def _log_record_exception(func):
    def _func(self):
        try:
            return func(self)
        except:
            log_data.exception('log_exception|thread=%s:%s,file=%s:%s,func=%s:%s,log=%s',
                               self.process, self.thread, self.filename, self.lineno, self.module, self.funcName,
                               self.msg)
            raise

    return _func


def append_exc(func):
    def _append_exc(*args, **kwargs):
        if 'exc_info' not in kwargs:
            kwargs['exc_info'] = True
        return func(*args, **kwargs)

    return _append_exc


def init_logger(log_dir=None, is_debug=False, is_test=False, rollover_when='MIDNIGHT',
                rollover_backup_count=30):
    # pylint: disable=too-many-locals

    if log_dir is None:
        log_dir = './log_api'

    import os
    import sys

    if log_dir != '@stdout':
        log_dir = os.path.abspath(log_dir)
        if log_dir and not os.path.exists(log_dir):
            os.mkdir(log_dir)

    logger_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': 'FastApiLog|%(asctime)s.%(msecs)03d|%(levelname)s|%(process)d:%(thread)d|%(filename)s:%(lineno)d|%(module)s.%(funcName)s|%(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'short': {
                'format': 'FastApiLog|%(asctime)s.%(msecs)03d|%(levelname)s|%(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'data': {
                'format': 'FastApiLog|%(asctime)s.%(msecs)03d|%(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'file_fatal': {
                'level': 'CRITICAL',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'fatal.log').replace('\\', '/'),
                'when': rollover_when,
                'backupCount': rollover_backup_count,
                'formatter': 'standard',
            },
            'file_error': {
                'level': 'WARNING',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'error.log').replace('\\', '/'),
                'when': rollover_when,
                'backupCount': rollover_backup_count,
                'formatter': 'standard',
            },
            'file_info': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'info.log').replace('\\', '/'),
                'when': rollover_when,
                'backupCount': rollover_backup_count,
                'formatter': 'short',
            },
            'file_data': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'data.log').replace('\\', '/'),
                'when': rollover_when,
                'backupCount': rollover_backup_count,
                'formatter': 'data',
            },
        },
        'loggers': {
            'main': {
                'handlers': ['file_fatal', 'file_error', 'file_info'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'data': {
                'handlers': ['file_data'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['file_fatal', 'file_error', 'file_info'],
                'level': 'ERROR',
                'propagate': True,
            },
            'tornado.access': {
                'handlers': ['file_data'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'tornado.application': {
                'handlers': ['file_fatal', 'file_error', 'file_info'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'tornado.general': {
                'handlers': ['file_fatal', 'file_error', 'file_info'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }

    if is_debug:
        logger_config['handlers']['file_debug'] = {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(log_dir, 'debug.log').replace('\\', '/'),
            'when': rollover_when,
            'backupCount': rollover_backup_count,
            'formatter': 'short',
        }
        logger_config['loggers']['django.db.backends'] = {
            'handlers': ['file_debug'],
            'level': 'DEBUG',
            'propagate': True,
        }
    elif not is_test:
        loggers = logger_config['loggers']
        for logger_item in loggers:
            if loggers[logger_item]['level'] == 'DEBUG':
                loggers[logger_item]['level'] = 'INFO'

    if log_dir == '@stdout':
        logger_config['handlers'] = {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'short',
            }
        }
        loggers = logger_config['loggers']
        for logger_item in loggers:
            loggers[logger_item]['handlers'] = ['console']

    work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
    recover_path = False
    if work_dir not in sys.path:
        sys.path.append(work_dir)
        recover_path = True

    import logging
    try:
        import logging.config
        logging.config.dictConfig(logger_config)
    except:
        from core import loggerconfig
        loggerconfig.dictConfig(logger_config)

    if recover_path:
        sys.path.remove(work_dir)

    global log_data  # pylint: disable=global-statement
    log_data = logging.getLogger('main')
    log_data.exception = append_exc(log_data.error)
    log_data.assertion = log_data.critical
    log_data.data = logging.getLogger('data').info
    logging.LogRecord.getMessage = _log_record_exception(logging.LogRecord.getMessage)


if log_data is None:
    from core.config import settings

    if settings is not None:
        setting_keys = dir(settings)
        if 'LOGGER_CONFIG' in setting_keys:
            init_logger(**settings.LOGGER_CONFIG)
        else:
            init_logger()
    else:
        init_logger()

