from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent
# Persist a per-installation development key across server restarts.
key_file = BASE_DIR / ".local-key"
if not os.environ.get("DJANGO_SECRET_KEY") and not key_file.exists():
    with key_file.open("x") as key:
        key.write(get_random_secret_key())
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or key_file.read_text()
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
ROOT_URLCONF = "urls"
INSTALLED_APPS = ["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "cases"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware"]
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "portal.sqlite3"}}
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
AUTH_PASSWORD_VALIDATORS = [{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"}]
LOGIN_URL = "/"
