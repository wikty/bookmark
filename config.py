import os
import urlparse



APP_ROOT = os.path.dirname(os.path.realpath(__file__))
PHANTOM = os.path.join(APP_ROOT, 'vendor/phantomjs/bin/phantomjs')
SCRIPT = os.path.join(APP_ROOT, 'screenshot.js')
MEDIA_ROOT = os.path.join(APP_ROOT, 'static/screenshots')
MEDIA_URL = '/static/screenshots/'
PERPAGE = 20

class Configuration(object):
	if 'PRODUCTION' in os.environ:
	    urlparse.uses_netloc.append('postgres') 
	    url = urlparse.urlparse(os.environ['DATABASE_URL'])

	    DATABASE = {
	        'engine': 'peewee.PostgresqlDatabase',
	        'name': url.path[1:],
	        'user': url.username,
	        'password': url.password,
	        'host': url.hostname,
	        'port': url.port,
	    }
	    DEBUG = False
	else:
	    DATABASE = {
	        'engine': 'peewee.PostgresqlDatabase',
	        'name': 'dog',
	        'user': 'dog',
	        'password': 'wiktymouse',
	        'host': 'localhost',
	        'port': 5432,
	        'threadlocals': True
	    }
    	DEBUG = True
