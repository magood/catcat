import os
from CatCat import create_app, db
from flask_script import Manager, Shell
from sqlalchemy.sql import text
from geoalchemy2 import *
from CatCat.models import Image, Location
from bot import reader
import logging

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db)
manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def init_db():
    db.drop_all()
    db.create_all()

@manager.command
def old_copy_data():
    thing = input("Press enter to start")
    #copy over initial data from catcat v1
    #old_query = text("""insert into catcat2.Image
    #    (entry_date, filename, address_text, loc, title, description, verified, rejected)
    #    select ml.entry_date, mls.filename, ml.address, PointFromText( CONVERT(AsText(ml.address_loc),CHAR(64)) ), ml.address, ml.comments, ml.approved, 0
    #    from mapmap.location ml
	   #     join mapmap.location_size mls on ml.location_id=mls.location_id and mls.size_code='ORIGINAL'
    #    where ml.approved=1;""");
    #Since DB refactoring to a Location table, single insert no longer works :(
    q = text("""select ml.entry_date, mls.filename, ml.address,
        AsText(ml.address_loc) loc_txt,
        ml.comments, ml.approved
        from mapmap.location ml
	        join mapmap.location_size mls on ml.location_id=mls.location_id and mls.size_code='ORIGINAL'
        where ml.approved=1;""")
    v1_images = db.session.execute(q).fetchall()
    for i in v1_images:
        #loc
        il = Location()
        wkt = i['loc_txt']
        il.loc = WKTSpatialElement(wkt)
        #image
        img = Image()
        img.entry_date = i['entry_date']
        img.filename = i['filename']
        img.address_text = i['address']
        img.title = i['address']
        img.description = i['comments']
        img.verified = i['approved'] == '1'
        img.rejected = 0
        
        img.location = il
        #il.image = img
        db.session.add(img);
    
    db.session.commit()

@manager.command
def test_mentions():
    thing = raw_input("Press enter to start")
    reader.get_mentions()
    pass

@manager.command
def twitter_import():
    #requests issues InsecurePlatformWarning that can't be resolved without adding software
    #I don't have permissions to add, or downgrading (not great either).  Suppress warnings.
    logging.captureWarnings(True)
    reader.get_mentions()

if __name__ == '__main__':
    manager.run()