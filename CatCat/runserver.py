"""
This script runs the CrumbCatalog application using a development server.
"""

import os
from CatCat import create_app, db
from CatCat.models import User
from flask_script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)