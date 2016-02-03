"""
CatCat web application package
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
#from . import config, Config as ConfigClass
from . import config
#from config import config, Config as ConfigClass
from flask_login import LoginManager

from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

db = SQLAlchemy()
manager = Manager()

lm = LoginManager()
authomatic = Authomatic(config.Config.OAUTH_PROVIDERS, 'random secret string for session signing')

def create_app(config_name=None):
    """creates a flask app instance using the given configuration"""
    app = Flask(__name__)
    if config_name is None:
        config_name = 'default'
    app.config.from_object(config.config[config_name])
    db.init_app(app)
    lm.init_app(app)
    lm.login_view = 'auth.login'

    #attach routes and custom error pages here
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    
    return app