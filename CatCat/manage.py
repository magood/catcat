import os
from CatCat import create_app, db
from flask_script import Manager, Shell
from sqlalchemy.sql import text
from geoalchemy2 import *
from CatCat.models import Image, Location
from bot import reader
import logging
from init_data import db_init

#app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(create_app)
#to manage production, for example: python manage.py -c production command_name
manager.add_option('-c', '--config', dest='config_name', required=False)

def make_shell_context():
    return dict(app=app, db=db)
manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def init_db():
    db.drop_all()
    db.create_all()
    
@manager.command
def import_data():
    thing = input("Press enter to start")
    db_init.load_images(db)

@manager.command
def test_mentions():
    thing = input("Press enter to start")
    reader.get_mentions()
    pass

@manager.command
def twitter_import():
    #requests issues InsecurePlatformWarning that can't be resolved without adding software
    #I don't have permissions to add, or downgrading (not great either).  Suppress warnings.
    #TODO investigate now that I'm on good hosting...
    logging.captureWarnings(True)
    reader.get_mentions()

if __name__ == '__main__':
    manager.run()