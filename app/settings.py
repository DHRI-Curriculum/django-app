import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set up SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY')

if SECRET_KEY == None:
    # Backup solution: read from app/.secrets/SECRET_KEY
    with open(os.path.join(BASE_DIR, 'app', '.secrets', 'SECRET_KEY')) as f:
        SECRET_KEY = f.read().strip()

# TODO: Is there a way to raise something other than a server 500 when SECRET_KEY fails here?

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'website.apps.WebsiteConfig',
    'workshop.apps.WorkshopConfig',
    'assessment.apps.AssessmentConfig',
    'resource.apps.ResourceConfig',
    'lesson.apps.LessonConfig',
    'learner.apps.LearnerConfig',
    'glossary.apps.GlossaryConfig',
    'feedback.apps.FeedbackConfig',
    'install.apps.InstallConfig',
    'insight.apps.InsightConfig',
    'backend',
    'adminsortable',
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.add_to_all_contexts',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


''' # MYSQL settings...
'ENGINE': 'django.db.backends.mysql',
'OPTIONS': {
    'read_default_file': os.path.join(BASE_DIR, 'sql.cnf'),
},
'TEST': {
    'NAME': 'dhinstit_curriculum_test',
},
'''


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATICFILE_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = '/home/dhinstit/static.dhinstitutes.org/curriculum'
STATIC_URL = '//static.dhinstitutes.org/curriculum/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SESSION_SAVE_EVERY_REQUEST = True

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_REDIRECT_URL = 'website:index'
LOGIN_URL = 'login'

EMAIL_PORT = 465
EMAIL_HOST = 'dhinstitutes.org'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

'''
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/home/dhinstit/.cache/django',
    }
}
'''
