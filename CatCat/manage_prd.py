import os

os.putenv('FLASK_CONFIG', 'production')

import manage

if __name__ == '__main__':
    manage.manager.run()