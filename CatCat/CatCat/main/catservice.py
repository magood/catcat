from CatCat.models import Image
from CatCat import db
import re

def get_all_cats():
    q = """select i.entry_date, ST_AsText(l.loc) wkt_loc,
	        i.title, i.description, i.filename
        from public."Image" i
            left join "Location" l on i.loc_id=l.id
        order by i.entry_date desc"""
    imgquery = db.session.execute(q).fetchall()
    images = [{
        'date': r.entry_date,
        'title': r.title,
        'filename': '/static/image_media/' + r.filename,
        'coords': get_coords(r['wkt_loc']),
        'description': r.description
    } for r in imgquery]
    return images

def get_coords(wkt):
    if (wkt != None):
        non_decimal = re.compile(r'[^\d. -]+')
        txt = non_decimal.sub('', wkt)
        parts = txt.split(' ')
        return (parts[0], parts[1])
    else:
        return None