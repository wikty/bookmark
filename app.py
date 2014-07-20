import os
import hashlib
import datetime
import subprocess
#import itertools
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%s'
)

# flask is a python microframework
# peewee is a python ORM
from flask import Flask, abort, redirect, render_template, request
from flask_peewee.db import Database
#from flask_peewee.utils import object_list, PaginatedQuery
from peewee import *

from middleman import upload_file, remove_file

APP_ROOT = os.path.dirname(os.path.realpath(__file__))
MEDIA_ROOT = os.path.join(APP_ROOT, 'static/screenshots')
MEDIA_URL = '/static/screenshots/'

# DATABASE = {
#     'name': os.path.join(APP_ROOT, 'bookmarks.db'),
#     'engine': 'peewee.SqliteDatabase'
# }

import urlparse
import psycopg2

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


PASSWORD = 'wiktymouse'
PHANTOM = os.path.join(APP_ROOT, 'vendor/phantomjs/bin/phantomjs')
SCRIPT = os.path.join(APP_ROOT, 'screenshot.js')
PERPAGE = 20

app = Flask(__name__)
app.config.from_object(__name__)
db = Database(app)

class Bookmark(db.Model):
    url = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    image = CharField(default='')

    class Meta:
        ordering = (('created_date', 'desc'), )

    def fetch_image(self):
        url_hash = hashlib.md5(self.url).hexdigest()
        filename = 'bookmark-%s.png' % url_hash

        outfile = os.path.join(MEDIA_ROOT, filename)
        params = [PHANTOM, SCRIPT, self.url, outfile]
        
        exitcode = subprocess.call(params)
        if exitcode == 0:
            remote_url = upload_file(outfile)
            if remote_url is not None:
                self.image = remote_url
                return

        # if fetch or upload failure, using a placeholder image
        self.image = os.path.join(MEDIA_ROOT, 'placeholder.png')
        

@app.route('/')
def index():
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception:
        page = 1

    query = Bookmark.select()
    bookmarks = []
    for bookmark in query:
        bookmarks.append(bookmark)
    
    total_pages = (len(bookmarks)+1) / PERPAGE
    start = PERPAGE * (page-1)
    end = max(page*PERPAGE, len(bookmarks))
    bookmarks = bookmarks[start:end]
    
    return render_template('index.html', **{'page': page,
                                            'total_pages': total_pages,
                                            'per_page': PERPAGE,
                                            'bookmarks': bookmarks
    })

@app.route('/add/')
def add():
    password = request.args.get('password')
    if password != PASSWORD:
        abort(404)

    url = request.args.get('url')
    if url:
        bookmark = Bookmark(url=url)
        bookmark.fetch_image()
        # logging.debug(bookmark.image)
        bookmark.save()
        return redirect(url)
    abort(404)

if __name__ == '__main__':
    # Create Bookmark database table if does not exist
    Bookmark.create_table(True)
    
    # Run application
    app.run()
