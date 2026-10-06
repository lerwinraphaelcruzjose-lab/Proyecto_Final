import os


class Config:
    """Configuración principal para desarrollo y producción."""
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///hotel.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "hotel-secreto-super-seguro-2026")
    WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "True").lower() in ("true", "1")


class TestingConfig(Config):
    """Configuración aislada para ejecución de pruebas automatizadas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False