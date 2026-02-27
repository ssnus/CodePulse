from .base import *

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost', 'web']

CSRF_TRUSTED_ORIGINS = [
    'http://0.0.0.0:8089',
    'http://127.0.0.1:8089',
    'http://localhost:8089',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Для удобства в dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'