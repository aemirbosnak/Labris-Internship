from logging.config import dictConfig


def configure_logging():
    # Logging configuration and formatting
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'flask.log',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['file']
        }
    })
