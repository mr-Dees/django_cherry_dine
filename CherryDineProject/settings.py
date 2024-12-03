from pathlib import Path

# Указываем корневую папку как 2 родителя от текущего файла
BASE_DIR = Path(__file__).resolve().parent.parent

# Настройка маршрутизации
ROOT_URLCONF = "CherryDineProject.urls"

# Настройка авторизации через модель пользователей
AUTH_USER_MODEL = 'CherryDineApp.User'

# Настройка для статических файлов(CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collectstatic'
STATICFILES_DIRS = [BASE_DIR / 'CherryDineApp' / 'static']

# Настройка для медиа файлов
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'CherryDineApp' / 'media'

# Настройки электронной почты
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'               # Используем smtp-сервер от yandex
EMAIL_USE_TLS = True                        # Включаем шифрование
EMAIL_PORT = 587                            # Задаем порт для отправки сообщений
EMAIL_HOST_USER = 'cherrydine@yandex.ru'    # Задаем логин (адрес) отправителя
EMAIL_HOST_PASSWORD = 'rqjdnigjmhzjpqre'    # Задаем пароль для авторизации на smtp-сервере
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER        # Задаем адрес отправителя по-умолчанию
SERVER_EMAIL = EMAIL_HOST_USER              # Задаем адрес отправителя для системных ошибок

# Настройка времени и региона
TIME_ZONE = "Asia/Novosibirsk"
USE_I18N = True
USE_TZ = True
LANGUAGE_CODE = "ru"

# Настройка установленных приложений (добавляем конфиг нашего приложения)
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'CherryDineApp.apps.CherrydineappConfig',
    'django_filters',
    'widget_tweaks',
]

# Настройка приложений по обработке запросов и ответов
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Шаблоны
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'CherryDineApp/templates'],
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

# База данных
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Режим отладки
DEBUG = True
# Разрешенный хосты (ограничений нет)
ALLOWED_HOSTS = []
# Настройка для развертывания на сервере
WSGI_APPLICATION = "CherryDineProject.wsgi.application"
# Секретный ключ
SECRET_KEY = "django-insecure-rtge*js2%*n2^&%#nk=9r&-co3l4c$6l1fw759ovfwo#prs@mp"
# Настройка первичного ключа по умолчанию
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Валидаторы паролей
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
