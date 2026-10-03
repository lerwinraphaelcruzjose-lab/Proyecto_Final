from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

database = SQLAlchemy()

migracion = Migrate()

aplicacion = Flask(__name__)

aplicacion.config.from_object("config.Config")

database.init_app(aplicacion)
migracion.init_app(aplicacion,database)

import app.models