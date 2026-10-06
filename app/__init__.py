from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

database = SQLAlchemy()
migracion = Migrate()
login_manager = LoginManager()

aplicacion = Flask(__name__)
aplicacion.config.from_object("config.Config")

database.init_app(aplicacion)
migracion.init_app(aplicacion, database)

# Configuración de Flask-Login
login_manager.init_app(aplicacion)
login_manager.login_view = "login"
login_manager.login_message = "Por favor, inicia sesión para acceder al sistema de gestión hotelera."
login_manager.login_message_category = "info"

import app.models


@login_manager.user_loader
def load_user(user_id: str):
    """Carga el usuario activo por su ID para Flask-Login."""
    return app.models.Usuario.query.get(int(user_id))


import app.routes