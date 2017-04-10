import tweepy
from CatCat import config
from CatCat.models import Image, Mention, TwitterLog, Location
from CatCat import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from geoalchemy2 import *
import requests
from PIL import Image as PIL_Image
from io import StringIO
import os

api = None

def get_mentions():
    global api
    if (api is None):
        auth = tweepy.OAuthHandler(config.Config.CATCAT_TWITTER_CONSUMER_KEY, config.Config.CATCAT_TWITTER_CONSUMER_SECRET)
        auth.set_access_token(config.Config.CATCAT_TWITTER_ACCESS_TOKEN, config.Config.CATCAT_TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
    last_run_max = get_last_id()
    mentions = api.mentions_timeline(count=20, since_id=last_run_max)
    since_id = None
    max_id = None
    for mention in reversed(mentions):
        #oldest first
        max_id = mention.id
        if since_id is None:
            since_id = mention.id
        print(mention.user.screen_name + ": " + mention.text)
        process_mention(mention)
    log_bot_run(since_id, max_id)

def log_bot_run(since_id, max_id):
    if since_id is not None:
        #insert into TwitterLog record of this run
        l = TwitterLog()
        l.tw_since_id = since_id
        l.tw_max_id = max_id
        db.session.add(l)
        db.session.commit()

def get_last_id():
    last_max = db.session.query(func.max(TwitterLog.tw_max_id)).scalar()
    return last_max

def process_mention(twm):
    m = Mention()
    m.tw_id = twm.id
    m.tw_text = twm.text
    m.tw_user_friendly_name = twm.user.name
    m.tw_username = twm.user.screen_name
    m.tw_profile_img_url = twm.user.profile_image_url
    m.tw_user_url = twm.user.url
    if twm.place is not None:
        m.tw_place_full_name = twm.place.full_name
        m.tw_place_type = twm.place.place_type
        #check this
        if twm.place.bounding_box:
            il = Location()
            lon = twm.place.bounding_box.coordinates[0][0][0]
            lat = twm.place.bounding_box.coordinates[0][0][1]
            wkt = "POINT({0} {1})".format(lon, lat)
            il.loc = WKTElement(wkt)
            m.tw_computed_location = il
            #todo average all points in bounding box? compute centroid?
    
    #Handle images
    if u'media' in twm.entities:
        for img in twm.entities[u'media']:
            #this really should be in the service somewhere since it will have to physically save an image to the FS, too.
            i = Image()
            i.filename = "{0}.jpg".format(twm.id)
            #location
            i.address_text = m.tw_place_full_name #'{0} {1}'.format(m.tw_place_full_name, twm.country)
            i.title = i.address_text
            i.description = m.tw_text
            base_img_url = img[u'media_url']
            img_url = "{0}:large".format(base_img_url)
            img_response = requests.get(img_url)
            p_img = PIL_Image.open(StringIO(img_response.content))
            cur_path = os.getcwd()
            outfile = os.path.join(cur_path, 'CatCat', 'static', 'image_media', i.filename)
            try:
                p_img.save(outfile)
            except IOError as e:
                print("cannot convert", i.title)
            i.mention_id = m.tw_id
            #associate a location with this image if we have one.
            i.location = m.tw_computed_location

            db.session.add(i)

    db.session.add(m)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


if __name__ == '__main__':
    get_mentions()