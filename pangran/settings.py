from pathlib import Path
import os
from dotenv import load_dotenv

# ==============================
# 🔹 Основные настройки
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()  # Загружаем .env

# ==============================
# 🔹 Критические настройки безопасности
# ==============================

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("ОШИБКА: DJANGO_SECRET_KEY не установлен в переменных окружения! Проверьте .env файл.")

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS - критически важно для production
ALLOWED_HOSTS_STR = os.getenv('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_STR:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]
else:
    # Если не установлен, используем безопасное значение по умолчанию только для разработки
    if DEBUG:
        ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    else:
        raise ValueError("ОШИБКА: ALLOWED_HOSTS не установлен в переменных окружения для production! Проверьте .env файл.")


# ==============================
# 🔹 Приложения
# ==============================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]


# ==============================
# 🔹 Middleware
# ==============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==============================
# 🔹 Настройки безопасности для production
# ==============================

if not DEBUG:
    # Безопасность для production
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # Если у вас есть SSL сертификат, раскомментируйте:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# ==============================
# 🔹 URL и WSGI
# ==============================

ROOT_URLCONF = 'pangran.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'pangran.wsgi.application'


# ==============================
# 🔹 База данных (SQLite по умолчанию)
# ==============================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==============================
# 🔹 Проверка паролей
# ==============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================
# 🔹 Локализация
# ==============================

LANGUAGE_CODE = 'ru-ru'  # Изменено на русский для вашего проекта
TIME_ZONE = 'Europe/Minsk'  # Беларусь
USE_I18N = True
USE_TZ = True


# ==============================
# 🔹 Статика
# ==============================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Медиа файлы (если используются)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==============================
# 🔹 Почта
# ==============================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Проверка настроек почты (опционально, можно закомментировать если почта не критична)
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    import warnings
    warnings.warn("ВНИМАНИЕ: EMAIL_HOST_USER или EMAIL_HOST_PASSWORD не установлены. Отправка почты не будет работать.")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'noreply@example.com'


# ==============================
# 🔹 ID по умолчанию
# ==============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
