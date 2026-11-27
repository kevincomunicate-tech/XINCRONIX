"""
Configuración del proyecto Xincronix (Django 5.2).

Los valores secretos o que cambian según el computador (clave secreta,
modo debug, hosts permitidos) se leen del archivo .env, que NO se sube
al repositorio. Usa .env.example como guía.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carpeta raíz del proyecto (donde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del archivo .env
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "solo-para-desarrollo-cambiame")

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# HTTPS: apagado en desarrollo (http://127.0.0.1). En producción, detrás de HTTPS, pon DJANGO_HTTPS=True.
HTTPS_ACTIVO = os.getenv("DJANGO_HTTPS", "False") == "True"
SECURE_SSL_REDIRECT = HTTPS_ACTIVO
SESSION_COOKIE_SECURE = HTTPS_ACTIVO
CSRF_COOKIE_SECURE = HTTPS_ACTIVO
SECURE_HSTS_SECONDS = 31536000 if HTTPS_ACTIVO else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = HTTPS_ACTIVO
SECURE_CONTENT_TYPE_NOSNIFF = True


# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Apps de Django
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Inicio de sesión con Google (django-allauth)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # Apps de Xincronix
    "cuentas",
    "dashboard",
    "comunicacion",
    "administracion",  # panel del superadministrador (politica_accesos.json)
    "sitio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Aplica "rutas_restringidas" de config/politica_accesos.json (va después de la autenticación)
    "cuentas.middleware.PoliticaAccesoMiddleware",
    # Lo exige django-allauth (inicio de sesión con Google)
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Plantillas compartidas (bases, páginas públicas)
        "DIRS": [BASE_DIR / "templates"],
        # Además busca en la carpeta templates/ de cada app
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cuentas.context_processors.politica_usuario",  # menú según el perfil
                "cuentas.context_processors.inicio_google",     # botón "Continuar con Google"
                "dashboard.context_processors.invitaciones",    # campana de invitaciones pendientes
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# Base de datos
#
# El motor se elige en .env con DB_ENGINE:
#   sqlite      -> un archivo db.sqlite3 en la carpeta del proyecto  [por defecto]
#   mysql       -> MySQL o MariaDB (XAMPP, MariaDB suelto, servidor)
#   postgresql  -> PostgreSQL
#
# Los MODELOS y las MIGRACIONES no cambian al cambiar de motor: Django
# traduce el mismo código Python al SQL de cada motor.
#
# Django NO usa phpMyAdmin: se conecta directo al servidor de base de datos.
# phpMyAdmin es solo una página web para ver esa misma base.
# Los datos de conexión se leen del archivo .env (no se sube a GitHub).
# ---------------------------------------------------------------------------

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").strip().lower()

if DB_ENGINE == "sqlite":
    # Un solo archivo; no necesita servidor, usuario ni contraseña.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("SQLITE_FILE", "db.sqlite3"),
        }
    }

elif DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",       # MySQL y MariaDB usan el mismo backend
            "NAME": os.getenv("DB_NAME", "xincronix_bd"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),   # XAMPP trae root sin contraseña
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),  # 127.0.0.1 = este mismo computador
            "PORT": os.getenv("DB_PORT", "3306"),       # 3306 en XAMPP; otro si cambiaste el puerto
            "OPTIONS": {
                "charset": "utf8mb4",                   # tildes, ñ y emojis
                # Rechaza datos inválidos en lugar de recortarlos en silencio
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            # Base separada para "python manage.py test": se crea y se borra sola,
            # así las pruebas nunca tocan los datos reales.
            "TEST": {
                "NAME": os.getenv("DB_TEST_NAME", "test_xincronix_bd"),
                "CHARSET": "utf8mb4",
                "COLLATION": "utf8mb4_unicode_ci",
            },
        }
    }

elif DB_ENGINE == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "xincronix_bd"),
            "USER": os.getenv("DB_USER", "xincronix_user"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),       # puerto por defecto de PostgreSQL
            "TEST": {"NAME": os.getenv("DB_TEST_NAME", "test_xincronix_bd")},
        }
    }

else:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        f"DB_ENGINE='{DB_ENGINE}' no es válido. Usa sqlite, mysql o postgresql en el archivo .env."
    )


# ---------------------------------------------------------------------------
# Ver el SQL que Django envía a la base (solo para aprender o depurar)
# Con DJANGO_LOG_SQL=True en .env y DEBUG activo, cada consulta (SELECT,
# INSERT, UPDATE...) se imprime en la terminal donde corre runserver.
# ---------------------------------------------------------------------------

if DEBUG and os.getenv("DJANGO_LOG_SQL", "False") == "True":
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"consola": {"class": "logging.StreamHandler"}},
        "loggers": {"django.db.backends": {"handlers": ["consola"], "level": "DEBUG"}},
    }


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

# Usuario propio: inicia sesión con correo en vez de "username"
AUTH_USER_MODEL = "cuentas.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        # Nombres de los ATRIBUTOS del modelo (las columnas se llaman nombres/apellidos)
        "OPTIONS": {"user_attributes": ("first_name", "last_name", "email")},
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "panel"  # respaldo: el inicio real de cada perfil sale del JSON

# Reglas de roles y rutas (quién es superadministrador, qué rol recibe el registro,
# a dónde entra cada perfil y qué rutas están restringidas). Sin "ifs" en el código.
POLITICA_ACCESOS = BASE_DIR / "config" / "politica_accesos.json"
# Qué muestra el panel de monitoreo del superadministrador (/administracion/monitoreo/)
MONITOREO = BASE_DIR / "config" / "monitoreo.json"
LOGOUT_REDIRECT_URL = "login"

# 1) correo + contraseña (nuestro login)   2) cuentas de Google (allauth)
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]


# ---------------------------------------------------------------------------
# Inicio de sesión con Google (django-allauth)
#
# Las credenciales se crean en Google Cloud Console (ver docs/integraciones.md)
# y se ponen en .env. Sin ellas el botón "Continuar con Google" aparece
# desactivado y el resto del sistema funciona igual.
# ---------------------------------------------------------------------------

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {"client_id": GOOGLE_CLIENT_ID, "secret": GOOGLE_CLIENT_SECRET},
        "SCOPE": ["openid", "profile", "email"],
        "AUTH_PARAMS": {"prompt": "select_account"},  # deja elegir la cuenta de Google
        "OAUTH_PKCE_ENABLED": True,
    }
}
# El usuario se identifica por su correo (no hay "username")
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
# Google ya verificó el correo: si existe una cuenta con ese correo, se vincula
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_STORE_TOKENS = False  # no guardamos tokens de Google: solo usamos el inicio de sesión
# La redirección separa el área administrativa y el espacio de proyectos.
ACCOUNT_ADAPTER = "cuentas.adaptadores.CuentaAdapter"
SOCIALACCOUNT_ADAPTER = "cuentas.adaptadores.GoogleAdapter"


# ---------------------------------------------------------------------------
# Asistente IA con Google Gemini (opcional)
#
# La clave se crea en Google AI Studio (ver docs/integraciones.md) y va en .env.
# Solo la usa el servidor: nunca llega al navegador. Sin clave, el asistente
# muestra cómo configurarlo y el resto del sistema funciona igual.
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
# El modelo se puede cambiar sin tocar el código (Google publica modelos nuevos seguido)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
# Si el modelo principal responde "saturado" (503), se intenta con estos, en orden (separados por coma). Vacío = sin respaldo.
GEMINI_MODEL_RESPALDO = os.getenv("GEMINI_MODEL_RESPALDO", "gemini-3.6-flash,gemini-3.5-flash-lite").strip()
# Preguntas por persona y por hora (protege la cuota gratuita de la clave)
GEMINI_LIMITE_POR_HORA = int(os.getenv("GEMINI_LIMITE_POR_HORA", "60"))


# ---------------------------------------------------------------------------
# GitHub (opcional)
#
# Sin token se pueden ver repositorios PÚBLICOS (GitHub permite 60 consultas por
# hora desde una misma IP). Con un token personal "fine-grained" de solo lectura
# el límite sube y también se ven los privados a los que el token tenga acceso.
# ---------------------------------------------------------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()


# ---------------------------------------------------------------------------
# Idioma y hora
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Archivos estáticos (CSS, JS, imágenes)
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
# Carpeta donde "collectstatic" junta todo para producción
STATIC_ROOT = BASE_DIR / "staticfiles"


# ---------------------------------------------------------------------------
# Archivos subidos por los usuarios (fotos de perfil)
# ---------------------------------------------------------------------------

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# Correo
# En desarrollo los correos (recuperar contraseña) se imprimen en la terminal.
# ---------------------------------------------------------------------------

EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "Xincronix <no-responder@xincronix.local>")
# Correo real (SMTP), por ejemplo Gmail con una "contraseña de aplicación".
# Se usa cuando DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend (ver docs/integraciones.md).
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_TIMEOUT = 15  # segundos: si el servidor de correo no responde, la invitación igual queda como notificación


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
