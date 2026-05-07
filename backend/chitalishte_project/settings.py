import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-in-production",
)

DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "core",
    "pages",
    "programs",
    "stories",
    "inquiries",
    "cms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chitalishte_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cms.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "chitalishte_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "bg"

TIME_ZONE = "Europe/Sofia"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_FROM_EMAIL = os.environ.get("DJANGO_DEFAULT_FROM_EMAIL", "webmaster@localhost")
INQUIRY_NOTIFICATION_ENABLED = env_bool("DJANGO_INQUIRY_NOTIFICATION_ENABLED", False)
INQUIRY_NOTIFICATION_RECIPIENTS = env_list("DJANGO_INQUIRY_NOTIFICATION_RECIPIENTS")
INQUIRY_NOTIFICATION_FROM_EMAIL = os.environ.get(
    "DJANGO_INQUIRY_NOTIFICATION_FROM_EMAIL",
    DEFAULT_FROM_EMAIL,
)
INQUIRY_NOTIFICATION_SUBJECT_PREFIX = os.environ.get(
    "DJANGO_INQUIRY_NOTIFICATION_SUBJECT_PREFIX",
    "[Народно читалище „Св. св. Кирил и Методий – 1926“]",
)

COOKIE_CONSENT_COOKIE_NAME = os.environ.get(
    "DJANGO_COOKIE_CONSENT_COOKIE_NAME",
    "chitalishte_cookie_preferences",
)
COOKIE_CONSENT_COOKIE_MAX_AGE = int(
    os.environ.get("DJANGO_COOKIE_CONSENT_COOKIE_MAX_AGE", str(60 * 60 * 24 * 180))
)
COOKIE_CONSENT_COOKIE_SECURE = env_bool("DJANGO_COOKIE_CONSENT_COOKIE_SECURE", not DEBUG)
COOKIE_CONSENT_COOKIE_HTTPONLY = env_bool("DJANGO_COOKIE_CONSENT_COOKIE_HTTPONLY", False)
COOKIE_CONSENT_COOKIE_SAMESITE = os.environ.get("DJANGO_COOKIE_CONSENT_COOKIE_SAMESITE", "Lax")

PUBLIC_SITE_URL = os.environ.get("DJANGO_PUBLIC_SITE_URL", "").rstrip("/")
