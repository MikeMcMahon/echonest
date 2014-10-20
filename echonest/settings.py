"""
Django settings for echonest project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!f2o3tj3z-upa=uoj81ovin+jxezw#&9day8zacxcm7t0i_8hn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'echonest',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'echonest.urls'

WSGI_APPLICATION = 'echonest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

if os.environ.get('PRODUCTION', None):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'echonest',
        'USER': os.environ.get('DBUSER', None),
        'PASSWORD': os.environ.get('DBPASS', None),
        'HOST': 'localhost'
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

INGESTER_HOME_DIR = '/data/home/steveo/'
INGESTER_API_DIR = '/root/echoprint-server/'

INGESTER_JSON_DIR = os.path.join(INGESTER_HOME_DIR, 'json-ingest')
INGESTER_BACK_DIR = os.path.join(INGESTER_HOME_DIR, '.json-backup')

UPLOADS_DIR = '/data/uploads/'

REMOTE_ENABLED = True
REMOTE_API_URL = 'http://pimp3d69-echoprint.cloudapp.net:8080/query?fp_code='
REMOTE_SOLR_URL = 'http://pimp3d69-echoprint.cloudapp.net:8502/solr/fp/select/?q=track_id:{0}*'