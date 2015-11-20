import sys, os  
INTERP = os.path.join(os.environ['HOME'], 'catcat.matthewcgood.com', 'env', 'bin', 'python')  
if sys.executable != INTERP:  
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
from CatCat import create_app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Uncomment next two lines to enable debugging
from werkzeug.debug import DebuggedApplication
application = DebuggedApplication(app, evalex=True)