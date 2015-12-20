import csv
from CatCat.models import User, Image, Location, Mention, TwitterLog
from geoalchemy2.elements import WKTElement
import os

def load_images(db):
    print("loading images...")
    with open('init_data\legacy_export\Image.csv', 'r', encoding="utf-8") as img_csvfile:
        reader = csv.DictReader(img_csvfile)
        for row in reader:
            #ignore mentions for now, handle below if you need them
            if row['mention_id'] == "NULL":
                entry_date = row['entry_date']
                filename = row['filename']
                address_text = row['address_text']
                title = row['title']
                description = row['description']
                verified = row['verified']
                rejected = row['rejected']
                loc_wkt = row['loc_wkt']
                il = Location()
                il.loc = WKTElement(loc_wkt, srid=4326) #4326 is "normal" lag/lng

                i = Image()
                i.entry_date = entry_date
                i.filename = filename
                i.address_text = address_text
                i.title = title
                i.description = description
                i.verified = verified
                i.rejected = rejected

                i.location = il
                db.session.add(i);
    print("committing...")
    db.session.commit()
    print("done")

#should I even bother with twitter or just start fresh?
def load_twitter_log(db):
    pass

def load_mentions(db):
    #handle mentions, and their associated images (excluded from load_images above)
    pass
