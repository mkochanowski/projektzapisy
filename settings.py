# Django settings for fereol project.

import os
import logging

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

RELEASE = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

"""
DATABASES = {
     'default' : {
        'ENGINE' : 'postgresql_psycopg2',
 	    'NAME' : 'fereol',
 	    'PORT' : '',
 	    'USER' : 'fereol',
	    'PASSWORD' : 'fereol',
 	    'HOST' : '',
 	    'CHARSET' : 'utf8',
 	    'USE_UNICODE' : True,
        }
 }
"""


DATABASES = {
     'default' : {
        'ENGINE' : 'sqlite3',
 	    'NAME' : os.path.join(PROJECT_PATH, 'database/db.sqlite3'),
 	    'PORT' : '',
 	    'USER' : '',
	    'PASSWORD' : '',
 	    'HOST' : '',
 	    'CHARSET' : 'utf8',
 	    'USE_UNICODE' : True,
        }
 }


# mass-mail account
# You can test sending with:
# $ python -m smtpd -n -c DebuggingServer localhost:1025

# For gmail:
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'youremail@gmail.com'
#EMAIL_HOST_PASSWORD = 'password'
#EMAIL_PORT = 587

#EMAIL_HOST = 'localhost'
#EMAIL_PORT = 1025
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''

EMAIL_COURSE_PREFIX = '[Fereol] ' # please don't remove the trailing space

#loggin settings:

#LOG_FILE = os.path.join(PROJECT_PATH, "logs/log.log")
#LOG_LEVEL = logging.NOTSET 
#INTERNAL_IPS = ('127.0.0.1',)
#logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE, format = '%(asctime)s | %(levelname)s | %(message)s')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,    
    'formatters': {
        'simple': {
            'format': '%(asctime)s | %(message)s'
        },
    },
    'handlers': {
        'standard_file': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'filename': os.path.join(PROJECT_PATH, 'logs/log.log'),
            'maxBytes': 104857600,
            'backupCount': 5,
            'formatter': 'simple'
        },
        'backup_file': {
            'class' : 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',

            'filename': os.path.join(PROJECT_PATH, 'logs/backup.log'),
            'maxBytes': 104857600,
            'backupCount': 5,
            'formatter': 'simple'
        }
     },
    'loggers': {
        'project.default': {
            'handlers': ['standard_file'],
            'level': 'INFO'
        },
        'project.backup': {
            'handlers': ['backup_file'],
            'level': 'INFO'

        }
    }
}

def custom_show_toolbar(request):
    if ('HTTP_HOST' in request.META) and (request.META['HTTP_HOST'][0:2] == 'm.'):
        return False
    return DEBUG

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar, 
    'INTERCEPT_REDIRECTS' : False,
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl-pl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'site_media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

USE_ETAGS = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '6$u2ggeh-!^hxep3s4h$3z&2-+3c@sy7-sy8349+l-1m)9r0fn'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#    'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'paranoidsessions.ParanoidSessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    #'middleware.mobile_detector.mobileDetectionMiddleware',
    #'middleware.mobileMiddleware.SubdomainMiddleware',
    'middleware.error_handling.ErrorHandlerMiddleware'
)

ROOT_URLCONF = 'fereol.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'haystack',
    'mailer',
    'south',
    'apps.enrollment.courses',
    'apps.enrollment.records',
    'apps.news',
    'apps.offer.preferences',
    'apps.offer.proposal',
    'apps.offer.vote',
    'apps.users',
    'debug_toolbar',
    'apps.grade.poll',
    'apps.grade.ticket_create',
    #'apps.mobile',
    'apps.email_change'
)

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'offer/proposal/fixtures'),
)

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/'

SKIP_SOUTH_TESTS = True # wylacza wbudowane testy south

HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_PATH, 'search_index')
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5

#TODO: udokumentowac zaleznosci!
#TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.run_tests'
#TEST_OUTPUT_VERBOSE = True
#TEST_OUTPUT_DESCRIPTIONS = True
#TEST_OUTPUT_DIR = 'xmlrunner'

#settings for enrollment
ECTS_LIMIT_DURATION = 14 # abs(t1-t2), in days
ECTS_BONUS = 5 # ECTS_BONUS * ECTS = abs(t0-t1); set to 7, if changed, change also get_t0_interval()
ECTS_LIMIT = 40

VOTE_LIMIT = 60

QUEUE_PRIORITY_LIMIT = 5

# that's only the example of settings_local.py file contents:
#SESSION_COOKIE_DOMAIN = '.localhost.localhost' # without port number!
SESSION_COOKIE_PATH = '/;HttpOnly'
#DEBUG = False
#TEMPLATE_DEBUG = DEBUG

SESSION_EXPIRE_AT_BROWSER_CLOSE	= True

DEBUG_TOOLBAR_ALLOWED_USERS = [
    "209067", # Tomasz Wasilczyk
    "209138", # Arkadiusz Flinik
    "208934",
    "gosia"
]

def show_toolbar(request):
    if request.user and request.user.username in DEBUG_TOOLBAR_ALLOWED_USERS:
        return True
    return False

DEBUG_TOOLBAR_CONFIG['SHOW_TOOLBAR_CALLBACK'] = show_toolbar

local_settings_file = os.path.join(PROJECT_PATH, 'settings_local.py')
if os.path.isfile(local_settings_file):
    execfile(local_settings_file)
