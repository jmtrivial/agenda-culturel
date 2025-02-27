from os import getenv as os_getenv, path as os_path # noqa
from pathlib import Path
from django.utils.translation import gettext_lazy as _

from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os_getenv(
    "SECRET_KEY", get_random_secret_key()
)  # If SECRET_KEY is not set, generate a random one
APP_ENV = os_getenv("APP_ENV", "dev")
DEBUG = os_getenv("DEBUG", "true").lower() in ["True", "true", "1", "yes", "y"]

ALLOWED_HOSTS = os_getenv("ALLOWED_HOSTS", "localhost").split(",")


if DEBUG:
    CSRF_TRUSTED_ORIGINS = os_getenv("CSRF_TRUSTED_ORIGINS", "http://localhost").split(
            ","
    )
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CSRF_TRUSTED_ORIGINS = os_getenv("CSRF_TRUSTED_ORIGINS", "http://localhost").split(
        ","
    )
    CORS_ALLOWED_ORIGINS = os_getenv("CORS_ALLOWED_ORIGINS", "http://localhost").split(
        ","
    )

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "agenda_culturel",
    "colorfield",
    'django_extensions',
    'django_better_admin_arrayfield',
    'django_filters',
    'compressor',
    'ckeditor',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    "corsheaders.middleware.CorsMiddleware",  # CorsMiddleware should be placed as high as possible,
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "agenda_culturel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "agenda_culturel.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os_getenv("POSTGRES_DB", "postgres"),
        "USER": os_getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os_getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os_getenv("POSTGRES_HOST", "db"),
        "PORT": os_getenv("POSTGRES_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ('en-us', _('English')),
    ('fr', _('French')),
)


# Auth

LOGIN_REDIRECT_URL = "/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os_path.join(BASE_DIR, "static")
MEDIA_URL = "media/"
MEDIA_ROOT = os_path.join(BASE_DIR, "media")

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Redis
REDIS_DB_KEYS = {
    "dev": 0,
    "test": 1,
    "prod": 2,
}

# Redis settingsEMAIL_USE_TLS

REDIS_HOST = os_getenv("REDIS_HOST", "redis")
REDIS_PORT = os_getenv("REDIS_PORT", 6379)

REDIS_DB = REDIS_DB_KEYS.get(APP_ENV, 0)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Celery settings

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# SCSS
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)


# EMAIL settings

if os_getenv("EMAIL_BACKEND"):
    EMAIL_BACKEND = os_getenv("EMAIL_BACKEND")
    EMAIL_HOST = os_getenv("EMAIL_HOST")
    EMAIL_PORT = os_getenv("EMAIL_PORT")
    EMAIL_HOST_USER = os_getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os_getenv("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = os_getenv("EMAIL_USE_TLS", False)
    EMAIL_USE_SSL = os_getenv("EMAIL_USE_SSL", False)
    DEFAULT_FROM_EMAIL = os_getenv("DEFAULT_FROM_EMAIL")
