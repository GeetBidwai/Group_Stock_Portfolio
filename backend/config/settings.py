from pathlib import Path
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
DJANGO_ENV = os.getenv("DJANGO_ENV", "development").strip().lower()
ALLOW_LOCAL_OTP_PREVIEW = os.getenv("ALLOW_LOCAL_OTP_PREVIEW", "false").lower() == "true"
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "*" if DEBUG else "localhost,127.0.0.1")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "apps.shared",
    "apps.auth_module",
    "apps.auth_telegram",
    "apps.portfolio_module",
    "apps.stock_search_module",
    "apps.stocks_module",
    "apps.analytics_module",
    "apps.comparison_module",
    "apps.risk_module",
    "apps.clustering_module",
    "apps.forecasting_module",
    "apps.sentiment_module",
    "apps.recommendations_module",
    "apps.commodities_module",
    "apps.crypto_module",
    "apps.assistant_module",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
AUTH_USER_MODEL = "auth_module.User"

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
            ]
        },
    }
]

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").strip().lower()

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", ""),
            "USER": os.getenv("POSTGRES_USER", ""),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", "60")),
        }
    }
else:
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
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Calcutta"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "true" if DEBUG else "false").lower() == "true"
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "stock-analytics-cache",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("apps.auth_module.authentication.CookieOrHeaderJWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

MARKET_DATA_PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "yfinance")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")
TELEGRAM_BOT_API_URL = os.getenv("TELEGRAM_BOT_API_URL", "https://api.telegram.org")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
TELEGRAM_SIGNUP_LINK_EXPIRY_SECONDS = int(os.getenv("TELEGRAM_SIGNUP_LINK_EXPIRY_SECONDS", "900"))
TELEGRAM_OTP_EXPIRY_SECONDS = int(os.getenv("TELEGRAM_OTP_EXPIRY_SECONDS", "300"))
TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS = int(os.getenv("TELEGRAM_OTP_RESEND_COOLDOWN_SECONDS", "60"))
OTP_VERIFIED_CACHE_SECONDS = int(os.getenv("OTP_VERIFIED_CACHE_SECONDS", "600"))
PASSWORD_RESET_OTP_MAX_ATTEMPTS = int(os.getenv("PASSWORD_RESET_OTP_MAX_ATTEMPTS", "3"))
PASSWORD_RESET_OTP_REQUEST_LIMIT_PER_HOUR = int(os.getenv("PASSWORD_RESET_OTP_REQUEST_LIMIT_PER_HOUR", "3"))
PASSWORD_RESET_TOKEN_EXPIRY_SECONDS = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRY_SECONDS", "600"))
AUTH_RESET_REQUIRE_OTP = os.getenv("AUTH_RESET_REQUIRE_OTP", "false").lower() == "true"
TELEGRAM_AUTH_MAX_AGE_SECONDS = int(os.getenv("TELEGRAM_AUTH_MAX_AGE_SECONDS", "86400"))

FEATURE_FLAGS = {
    "enable_portfolio": os.getenv("FF_ENABLE_PORTFOLIO", "true").lower() == "true",
    "enable_comparison": os.getenv("FF_ENABLE_COMPARISON", "true").lower() == "true",
    "enable_risk": os.getenv("FF_ENABLE_RISK", "true").lower() == "true",
    "enable_clustering": os.getenv("FF_ENABLE_CLUSTERING", "true").lower() == "true",
    "enable_forecasting": os.getenv("FF_ENABLE_FORECASTING", "true").lower() == "true",
    "enable_sentiment": os.getenv("FF_ENABLE_SENTIMENT", "true").lower() == "true",
    "enable_commodities": os.getenv("FF_ENABLE_COMMODITIES", "true").lower() == "true",
    "enable_crypto": os.getenv("FF_ENABLE_CRYPTO", "true").lower() == "true",
}

RISK_THRESHOLDS = {
    "low": 0.01,
    "medium": 0.02,
}

if not DEBUG:
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "true").lower() == "true"
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "false").lower() == "true"
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "false").lower() == "true"
    SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "false").lower() == "true"
