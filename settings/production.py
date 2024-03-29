from .base import *

DEBUG = False
USE_SOCIAL_AUTH = not DEBUG
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.compute.amazonaws.com', 'abstracts.abacbs.org']

# See https://docs.djangoproject.com/en/0.11/ref/settings/#secure-proxy-ssl-header
# for security risks related to SSL headers. Set these only if you are using the
# NGINX proxy.
# Enable use of forwarded scheme, host and port from nginx/apache when proxying
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Loggers setup.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'info.log'),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True
        },
    },
}

# Host for sending e-mail
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = get_secret('email_host')
# EMAIL_PORT = get_secret('email_port')
# REPLY_TO_EMAIL = get_secret('reply_to_email')
#
# # Optional SMTP authentication information for EMAIL_HOST
# EMAIL_HOST_USER = get_secret('email_host_user')
# EMAIL_HOST_PASSWORD = get_secret('email_host_password')
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True
