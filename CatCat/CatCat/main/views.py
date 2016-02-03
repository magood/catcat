from datetime import datetime
from flask import render_template, jsonify, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
import os
from . import main
from . import catservice, uploadhelper
from CatCat.models import Image, Location
from CatCat import db
from . import forms
from decimal import *
from geoalchemy2.elements import WKTElement

from werkzeug.utils import secure_filename

@main.route('/')
@main.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'main/index.html',
        title='I Heart Heart Cat Cat Map Map App App',
        year=datetime.now().year,
    )

@main.route("/api/cats")
def api_cats():
    images = catservice.get_all_cats()
    return jsonify(cats = images)

@main.route("/api/nearby_cats/<int:cat_id>")
def api_nearby_cats(cat_id):
    cat = db.session.query(Image).get(cat_id)
    nearby = catservice.get_nearby(cat.location.loc, cat_id, 4)
    return jsonify(nearby = nearby)

@main.route('/cats')
def cats():
    """Renders the All Cat Cats page."""
    mycats = catservice.get_all_cats()

    return render_template(
        'main/allcats.html',
        title='All Cats - I Heart Heart Cat Cat',
        year=datetime.now().year,
        allcats = mycats
    )

@main.route('/image/<int:id>', methods=('GET', 'POST'))
def image(id):
    cat = db.session.query(Image).get(id)

    return render_template(
        'main/image.html',
        title='CatCat Sighting',
        cat=cat
    )

@main.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    """Page to add a new catcat sighting."""
    form = forms.NewSightingForm()
    if form.validate_on_submit():
        file = request.files['imageFile']
        if file and uploadhelper.allowed_file(file.filename):
            filename = uploadhelper.save_with_rename(file)

            #Create the DB model objects
            i = Image()
            i.creator = current_user
            i.address_text = form.address.data
            i.title = form.title.data
            i.description = form.description.data
            i.filename = filename
            l = Location()
            #Safety first. They should already but Decimals, but double-check.
            lng = Decimal(form.loc_lng.data)
            lat = Decimal(form.loc_lat.data)
            #POINT(lng lat)
            loc_wkt = "POINT({0} {1})".format(lng, lat)
            l.loc = WKTElement(loc_wkt, srid=4326) #4326 is "normal" lag/lng
            i.location = l
            db.session.add(i)
            db.session.commit()

            new_id = i.id
            return redirect(url_for('main.image', id=new_id))
        else:
            flash("File type not allowed.")
    #otherwise...
    return render_template(
        'main/upload.html',
        title='Add A Cat',
        form=form
    )

#@main.route('/process_upload', methods=['POST'])
#@login_required
#def process_upload():
#    file = request.files['file']
#    if file and uploadhelper.allowed_file(file.filename):
#        filename = secure_filename(file.filename)
#        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
#        return redirect(url_for('uploaded_file',
#                                filename=filename))

@main.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About - I Heart Heart Cat Cat',
        year=datetime.now().year,
        message='Your application description page.'
    )

@main.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact - I Heart Heart Cat Cat',
        year=datetime.now().year,
        message='Your contact page.'
    )