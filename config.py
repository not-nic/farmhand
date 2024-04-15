import os


class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = "mysql://root:password@localhost:3306/farmhand"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_PATH = "static"
