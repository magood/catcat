from datetime import datetime
from flask import render_template, jsonify
from . import main
from . import catservice
from CatCat.models import Image, Location
from CatCat import db

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