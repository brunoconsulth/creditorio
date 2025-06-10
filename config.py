# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave-super-secreta')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///precatorios.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
