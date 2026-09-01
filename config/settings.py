"""
Django settings for the Salon E-Commerce & Service Booking Platform.
"""
import os
from datetime import timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from backend/.env
load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-2sy$g!+@h%k^iqmp0_i_g=83%vsnwuj9e5en13%9-60bo_76ix")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if host.strip()]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    # Local apps
    "accounts",
    "customers",
    "staff",
    "categories",
    "products",
    "services",
    "carts",
    "orders",
    "appointments",
    "payments",
    "reviews",
    "notifications",
    "reports",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database Configuration
# Automatically supports:
# 1. DATABASE_URL (Render PostgreSQL or external database URL) via dj_database_url
# 2. Explicit MySQL environment variables (DB_ENGINE=django.db.backends.mysql)
# 3. Local SQLite default
DATABASE_URL = os.getenv("DATABASE_URL")
DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
        if DATABASES["default"].get("ENGINE") == "django.db.backends.mysql":
            import pymysql
            pymysql.install_as_MySQLdb()
    except Exception:
        DATABASE_URL = None

if not DATABASE_URL:
    if DB_ENGINE == "django.db.backends.mysql":
        import pymysql

        pymysql.install_as_MySQLdb()
        
        db_host = os.getenv("DB_HOST", "127.0.0.1").strip().strip("'\"")
        db_port = os.getenv("DB_PORT", "3306").strip().strip("'\"")
        db_name = os.getenv("DB_NAME", "salon_db").strip().strip("'\"")
        db_user = os.getenv("DB_USER", "root").strip().strip("'\"")
        db_pass = os.getenv("DB_PASSWORD", "").strip().strip("'\"")

        # Strip protocol if accidentally included in DB_HOST (e.g., mysql://...)
        if "://" in db_host:
            db_host = db_host.split("://")[-1]
        if "/" in db_host:
            db_host = db_host.split("/")[0]

        # Extract port if host was entered as host.aivencloud.com:28608
        if ":" in db_host and not db_host.startswith("["):
            host_parts = db_host.split(":")
            db_host = host_parts[0]
            db_port = host_parts[1]

        db_options = {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        }

        # Aiven MySQL requires SSL
        ssl_mode = os.getenv("DB_SSL_MODE", "").upper()
        if ssl_mode or "aivencloud.com" in db_host:
            db_options["ssl"] = {"ssl_mode": ssl_mode or "REQUIRED"}

        DATABASES = {
            "default": {
                "ENGINE": DB_ENGINE,
                "NAME": db_name,
                "USER": db_user,
                "PASSWORD": db_pass,
                "HOST": db_host,
                "PORT": db_port,
                "OPTIONS": db_options,
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": DB_ENGINE,
                "NAME": os.getenv("DB_NAME", str(BASE_DIR / "db.sqlite3")),
            }
        }


AUTH_USER_MODEL = "accounts.User"

# Password validation
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
LANGUAGE_CODE = "en-us"

TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
}

# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", 60))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", 7))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# CORS
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL", "False").lower() == "true"

raw_cors = os.getenv("CORS_ALLOWED_ORIGINS", "")
if raw_cors:
    origins = []
    for item in raw_cors.split(","):
        item = item.strip()
        if item:
            if not item.startswith("http://") and not item.startswith("https://"):
                item = f"https://{item}"
            origins.append(item)
    CORS_ALLOWED_ORIGINS = origins
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://saloon-fe.vercel.app",
    ]

# Automatically allow Vercel domains (production & previews) and Render frontend apps
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://.*\.onrender\.com$",
]

CORS_ALLOW_CREDENTIALS = True

# Salon business rules
SALON_OPENING_TIME = "09:00"
SALON_CLOSING_TIME = "19:00"

# Email console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Razorpay. Leave the keys blank to run without a gateway: payments then stay
# pending and are reconciled by hand on the admin payments screen.
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_CURRENCY = os.getenv("RAZORPAY_CURRENCY", "INR")
