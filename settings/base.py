"""
Django settings for ABACBSAbsSS project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import json
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(str(Path(__file__))).parents[1]
SETTINGS_DIR = BASE_DIR / "settings"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Read the secrets file
try:
    with open(str(SETTINGS_DIR / "secrets.json"), 'rt') as handle:
        secrets = json.load(handle)
except FileNotFoundError:
    raise FileNotFoundError("You must create a 'secrets.json' file in the "
                            "project settings directory.")


def get_secret(setting, secrets=secrets):
    """
    Retrieve a named setting from the secrets dictionary read from the JSON.
    Adapted from Two Scoops of Django, Example 5.21
    """
    try:
        return secrets[setting]
    except KeyError:
        error_message = "Unable to retrieve setting: '{}'".format(setting)
        raise ImproperlyConfigured(error_message)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('secret_key')

# Social auth settings for ORCID authentication
SOCIAL_AUTH_ORCID_PROFILE_EXTRA_PARAMS = {'credit-name': 'credit_name'}
SOCIAL_AUTH_ORCID_KEY = get_secret('orcid_key')
SOCIAL_AUTH_ORCID_SECRET = get_secret('orcid_secret')
SOCIAL_AUTH_USER_MODEL = 'auth.User'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/profile/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/orcid/error/"
SOCIAL_AUTH_URL_NAMESPACE = 'account:social'
SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    # 'social_core.pipeline.social_auth.load_extra_data',
    # adds credit-name as credit_name to extra data in the social auth
    # profile model
    'core.pipeline.orcid_load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.social_auth.associate_by_email',
    'core.pipeline.assign_group',
]


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'social_core.backends.orcid.ORCIDOAuth2'
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'index',
    'demographic',
    'account',
    'abstract',

    'social_django',
    'rest_framework',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Social-auth middleware
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'ABACBSAbsSS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # Custom
                "core.context_processors.user_groups",
                "core.context_processors.assignment_status",
                "core.context_processors.categories",

                # Social-auth context_processors
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'ABACBSAbsSS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Melbourne'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR / 'static/')

# Redirect to home URL after login (Default redirects to /profile/)
LOGIN_REDIRECT_URL = 'account:profile'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'account:orcid_login'


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '250/day',
        'user': '1000/day'
    },
}


# DEBUG email server, set to something proper when DEBUG = FALSE
DEFAULT_FROM_EMAIL = "committee@abacbs.org"
SERVER_EMAIL = "committee@abacbs.org"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CLOSING_DATE = '2018-09-28 09:00:00+10:00'
SCHOLARSHIP_CLOSING_DATE = '2018-09-17 09:00:00+10:00'
