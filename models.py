import os
import datetime
import subprocess

from hashlib import md5

from flask_peewee.auth import BaseUser
from peewee import *

from app import db
from filedeliver import upload_file, remove_file


def initdb():
    # Create tables if does not exist
    User.create_table(True)
    Bookmark.create_table(True)
    Tag.create_table(True)
    Relationship.create_table(True)
    
    # add admin user
    if(not User.select().where(username=='asdfghjkl999',
                               email=='xiaowenbin_999',
                               admin==True,
                               active==True
            ).exists()):
        admin = User.create(username='asdfghjkl999', email='xiaowenbin_999@163.com', admin=True, active=True)
        admin.set_password('asdfghjkl999')
        admin.save()


class User(db.Model, BaseUser):
    username = CharField()
    password = CharField()
    email = CharField()
    join_date = DateTimeField(default=datetime.datetime.now)
    active = BooleanField(default=True)
    admin = BooleanField(default=False)

    def __unicode__(self):
        return self.username

    def gravatar_url(self, size=80):
        return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
            (md5(self.email.strip().lower().encode('utf-8')).hexdigest(), size)

class Bookmark(db.Model):
    url = CharField()
    created_date = DateTimeField(default=datetime.datetime.now)
    image = CharField(default='')
    title = CharField(default='')
    # a user instance, user.Bookmarks == Bookmark.select().where(user=user)
    user = ForeignKeyField(User, related_name='Bookmarks')

    class Meta:
        order_by = ('-created_date', )
    
    def __unicode__(self):
        return self.url

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
        self.image = os.path.join('/static/img', 'placeholder.png')

    def fetch_bookmarks(self, tag=None):
        # tag is Tag's id
        if tag is not None:
            return Bookmark.select().join(
                Relationship, on=Relationship.bookmark
            ).where(Relationship.tag==tag).order_by(Bookmark.created_date)
        else:
            return Bookmark.select()

    def search_bookmarks(self, kw):
        if kw:
            kw = '%'+kw+'%'
        else:
            kw = 'aklsfdklsjkdksiwwo'
        return Bookmark.select().where(Bookmark.title % kw)

class Tag(db.Model):
    name = CharField()
    # a user instance, user.Tags == Tag.select().where(user=user)
    user = ForeignKeyField(User, related_name='Tags')

    class Meta:
        order_by = ('name', )

    def fetch_tags(self, bookmark=None):
        # bookmark is Bookmark's id
        if bookmark is not None:
            return Tag.select().join(
                Relationship, on=Relationship.tag
            ).where(Relationship.bookmark==bookmark).order_by(Tag.name)
        else:
            return Tag.select()


class Relationship(db.Model):
    user = ForeignKeyField(User)
    tag = ForeignKeyField(Tag)
    bookmark = ForeignKeyField(Bookmark)

    def __unicode__(self):
        return 'Bookmark %s has Tag[%s]' % (self.bookmark, self.tag)
