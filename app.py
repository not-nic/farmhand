import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

database = SQLAlchemy()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:password@localhost:3306/farmhand"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["STATIC_PATH"] = "static"
database.init_app(app)

from scripts import equipment_util
from blueprints.fields import fields
app.register_blueprint(equipment_util.equipment_util)
app.register_blueprint(fields)

with app.app_context():
    database.create_all()
    # Run on startup and parse vehicles from Farming Simulator.
    equipment_util.collect_equipment()


@app.route("/")
def index():
    return jsonify({"message": "Hello World!"}), 200


if __name__ == "__main__":
    app.run(debug=True)
