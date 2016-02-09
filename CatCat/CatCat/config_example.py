import os
from authomatic.providers import oauth2
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = False
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or "some key"
    #PREFERRED_URL_SCHEME = 'https'
    
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = '/path/to/the/uploads'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

    OAUTH_PROVIDERS = {
        'google': {
            'class_': oauth2.Google,
            'consumer_key': '########################',
            'consumer_secret': '########################',
            'scope': oauth2.Google.user_info_scope,
        },
        'fb': {
            'class_': oauth2.Facebook,
            # Facebook is an AuthorizationProvider so we need to set several other properties too:
            'consumer_key': '########################',
            'consumer_secret': '########################',
            # It is also an OAuth 2.0 provider and it needs scope.
            'scope': ['user_about_me', 'email', 'publish_stream'],
        }
    }

    CATCAT_TWITTER_CONSUMER_KEY = "########################"
    CATCAT_TWITTER_CONSUMER_SECRET = "########################"
    CATCAT_TWITTER_ACCESS_TOKEN = "########################"
    CATCAT_TWITTER_ACCESS_SECRET ="########################"

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or ''

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRD_DATABASE_URI') or ''

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}