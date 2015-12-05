from CatCat import db
from sqlalchemy import Column, BigInteger, Integer, SmallInteger, String, Date, DateTime, ForeignKey, Float, Boolean
from geoalchemy2 import *
import datetime
import re

class User(db.Model):
    __tablename__ = 'User'
    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), index=True, unique=True, nullable=False)
    email = Column(String(120), index=True, unique=True, nullable=False)
    display_name = Column(String(120))
    twitter_id = Column(String(20), index=True)
    #ensure you're passing the FUNCTION utcnow as default, not the value returned from it.
    entry_date  = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    images = db.relationship('Image', backref='creator')

    #flask login methods
    #http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    #is authenticated is misleading for OpenID
    #should return true unless not alowed to auth for some reason.
    #TODO is this the same for OAuth which I'm now using?
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.username)

class Location(db.Model):
    """Purely to model a location - other tables will join here instead of defining their own loc"""
    __tablename__ = 'Location'
    __table_args__ = {'mysql_engine':'MyISAM','mysql_charset':'utf8'}
    id = Column(BigInteger, primary_key=True)
    loc = Column(Geometry('POINT'))
    #image = db.relationship('Image', backref='location', foreign_keys=['loc_id'])
    #other backrefs?

class Image(db.Model):
    __tablename__ = 'Image'
    id = Column(BigInteger, primary_key=True)
    entry_date  = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    creator_id = Column(BigInteger, ForeignKey('User.id'), index=True, nullable=True)
    mention_id = Column(BigInteger, ForeignKey('Mention.tw_id'), index=True, nullable=True)
    filename = Column(String(64))
    loc_id = Column(BigInteger, ForeignKey('Location.id'), index=True, nullable=True)
    location = db.relationship("Location", foreign_keys=[loc_id])
    address_text = Column(String(80))
    title = Column(String(80))
    description = Column(String(256))
    exif_loc_id = Column(BigInteger, ForeignKey('Location.id'), index=True, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    rejected = Column(Boolean, default=False, nullable=False)

class Mention(db.Model):
    __tablename__ = 'Mention'
    tw_id = Column(BigInteger, primary_key=True, autoincrement=False) #twitter's id
    entry_date  = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    tw_text = Column(String(140), nullable=False)
    tw_user_friendly_name = Column(String(140), nullable=False)
    tw_username = Column(String(20), index=True, nullable=False)
    tw_profile_img_url = Column(String(255))
    tw_user_url = Column(String(255))
    tw_place_full_name = Column(String(511))
    tw_place_type = Column(String(100))
    tw_computed_loc_id = Column(BigInteger, ForeignKey('Location.id'), index=True, nullable=True)
    tw_computed_location = db.relationship("Location", foreign_keys=[tw_computed_loc_id])
    images = db.relationship('Image', backref='mention')

class TwitterLog(db.Model):
    __tablename__ = 'TwitterLog'
    id = Column(BigInteger, primary_key=True)
    entry_date  = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    tw_since_id = Column(BigInteger) #twitter's id
    tw_max_id = Column(BigInteger) #twitter's id

#GeometryDDL(Location.__table__)