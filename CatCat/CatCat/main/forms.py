from flask_wtf import Form
from wtforms import StringField, validators, TextAreaField, HiddenField, FileField, DecimalField
from wtforms.widgets import HiddenInput

class NewSightingForm(Form):
    address = StringField('Address', [validators.InputRequired(), validators.Length(max=80)])
    loc_lat = DecimalField('Latitude', [validators.InputRequired(), validators.NumberRange(min=-90, max=90)], widget=HiddenInput())
    loc_lng = DecimalField('Longitude', [validators.InputRequired(), validators.NumberRange(min=-180, max=180)], widget=HiddenInput())
    title = StringField('Title', [validators.InputRequired(), validators.Length(max=80)])
    description = TextAreaField('Description', [validators.Length(max=256)])
    imageFile = FileField('Image File', [validators.InputRequired("An image file is required.")])