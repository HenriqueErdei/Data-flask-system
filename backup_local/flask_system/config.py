import os

SECRET_KEY = os.environ.get('SECRET_KEY', '8f9d8f7a9sd8f7a9sd8f7a9sd8f7a9sd8f7a9sd8f7a9sd8f7a9sd8f7a9sd8f7a')
DATA_PATH = 'data/'
LOG_PATH = DATA_PATH + 'logs/'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'database.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
