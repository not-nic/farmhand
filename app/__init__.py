from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

database = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    database.init_app(app)

    from scripts import equipment_util
    app.register_blueprint(equipment_util.equipment_util)

    from blueprints.fields import fields
    app.register_blueprint(fields)

    from scripts import crop_util

    with app.app_context():
        database.create_all()
        # Load all crop types in farming simulator
        crop_util.load_crops()
        # Run on startup and parse vehicles from Farming Simulator.
        equipment_util.collect_equipment()

    return app
