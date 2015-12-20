﻿from CatCat.models import Image, Location
from CatCat import db
import re

def get_all_cats():
    q = """select i.id, i.entry_date, ST_AsText(l.loc) wkt_loc,
	        i.title, i.description, i.filename
        from public."Image" i
            left join "Location" l on i.loc_id=l.id
        order by i.entry_date desc"""
    imgquery = db.session.execute(q).fetchall()
    images = [{
        'id': r.id,
        'date': r.entry_date,
        'title': r.title,
        'filename': '/static/image_media/' + r.filename,
        'coords': get_coords(r['wkt_loc']),
        'description': r.description
    } for r in imgquery]
    return images

def get_nearby(spot, id=None, n=5):
    n = min(n, 10)
    #wkt_spot = "POINT({0} {1})".format(lat, lng)
    #spot = geom=WKTSpatialElement(wkt_spot)
    closest_query = db.session.query(Image, Location.loc.ST_Distance_Sphere(spot).label("distance"), Location.loc.ST_AsText().label("wkt")).join(Image.location).filter(Image.id != id).order_by(Location.loc.ST_Distance_Sphere(spot)).limit(n)
    #c = list(closest_query)
    near = [{
        'id': r.Image.id,
        'title': r.Image.title,
        'distance': r.distance,
        'filename': '/static/image_media/' + r.Image.filename,
        'coords': get_coords(r.wkt)
    } for r in closest_query]
    return near

def get_coords(wkt):
    if (wkt != None):
        non_decimal = re.compile(r'[^\d. -]+')
        txt = non_decimal.sub('', wkt)
        parts = txt.split(' ')
        return (parts[0], parts[1])
    else:
        return None