import os, uuid
from werkzeug.utils import secure_filename
from flask import current_app
from CatCat import config

def get_ext(filename):
    _, ext = os.path.splitext(filename)
    if ext and len(ext) > 0:
        ext = ext[1:]
        ext = ext.lower()
    return ext

def allowed_file(filename):
    """crude file type validation - TODO move to a custom wtforms validator"""
    ext = get_ext(filename)
    return ext and ext in current_app.config['ALLOWED_EXTENSIONS']

def get_candidate_fn(ext):
    u = uuid.uuid4()
    ustr = secure_filename(str(u) + "." + ext)
    folder = current_app.config['UPLOAD_FOLDER']
    return folder, ustr

def get_unique_fn(ext):
    fpath, fn = get_candidate_fn(ext)
    while os.path.isfile(fpath):
        fpath, fn = get_candidate_fn(ext)
    return fpath, fn

def save_with_rename(file):
    """Save file (FileStorage object) with a unique filename"""
    ext = get_ext(file.filename)
    path, fn = get_unique_fn(ext)
    file.save(os.path.join(path, fn))
    return fn