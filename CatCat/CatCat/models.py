from CatCat import db
from flask import current_app
from sqlalchemy import Column, BigInteger, Integer, SmallInteger, String, Date, DateTime, ForeignKey, Float, Boolean
from geoalchemy2 import *
import datetime
import re

class Permission:
    NONE = 0x00
    VERIFY_IMAGE = 0x01
    REJECT_IMAGE = 0x02
    EDIT_IMAGE = 0x04
    ADMINISTER = 0x08

class Role(db.Model):
    __tablename__ = 'Role'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    default = Column(Boolean, default=False)
    permissions = Column(Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.NONE, True),
            'Administrator':(0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

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
    role_id = Column(BigInteger, ForeignKey('Role.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_USER_EMAIL']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    #permissions
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

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
    loc = Column(Geometry('POINT', srid=4326)) #4326 means "normal" WGS84 lat/long
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