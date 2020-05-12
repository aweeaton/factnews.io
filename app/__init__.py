from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import shutil
import nltk

# Create an application instance (an object of class Flask) to handle reqs
application = Flask(__name__)
application.config.from_object(Config)
db = SQLAlchemy(application)
db.create_all()
db.session.commit()

# login_manager needs to be initiated before running the app
login_manager = LoginManager()
login_manager.init_app(application)

# initalize Bootstrap
bootstrap = Bootstrap(application)

# # Download nltk data
DOWNLOAD_DIR = '/tmp/'
nltk.download('punkt', download_dir=DOWNLOAD_DIR)
nltk.download('averaged_perceptron_tagger', download_dir=DOWNLOAD_DIR)
nltk.download('universal_tagset', download_dir=DOWNLOAD_DIR)

# Added at the bottom to avoid circular dependencies. (Violates PEP8 standards)
from app import classes
from app import routes
