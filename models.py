import os
import re
import hashlib
import datetime
import subprocess

from flask_peewee.auth import BaseUser
from peewee import *

from app import db
from config import *
from filedeliver import upload_file, remove_file

class User(db.Model, BaseUser):
    username = CharField()
    password = CharField()
    email = CharField()
    introduction = CharField(default='')
    join_date = DateTimeField(default=datetime.datetime.now)
    active = BooleanField(default=True)
    admin = BooleanField(default=False)

    def __unicode__(self):
        return self.username

    def gravatar_url(self, size=80):
        return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
            (hashlib.md5(self.email.strip().lower().encode('utf-8')).hexdigest(), size)

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
            # May be should add try again
            remote_url = upload_file(outfile)
            if remote_url is not None:
                self.image = remote_url
        
        # if fetch or upload failure, using a placeholder image
        if not self.image:
            self.image = os.path.join('/static/img', 'placeholder.png')
        
        # remove generated local file
        if os.path.isfile(outfile):
            os.unlink(outfile)

    def destory_image(self):
        remove_file(self.image)
    
    def fetch_tags(self):
        return Tag.select().join(Relationship).join(Bookmark).where(Bookmark.url == self.url)
    
    def fetch_owner(self):
        return User.select().where(User.id == self.user).get()

class Tag(db.Model):
    name = CharField()
    # a user instance, user.Tags == Tag.select().where(user=user)
    user = ForeignKeyField(User, related_name='Tags')

    class Meta:
        order_by = ('name', )
    
    def __unicode__(self):
        return self.name

    def fetch_bookmarks(self):
        return Bookmark.select().join(Relationship).join(Tag).where(Relationship.user == self.user, Tag.name == self.name)
    
    def fetch_owner(self):
        return User.select().where(User.id == self.user).get()

class Relationship(db.Model):
    user = ForeignKeyField(User)
    tag = ForeignKeyField(Tag, related_name='Bookmarks')
    bookmark = ForeignKeyField(Bookmark, related_name='Tags')

    def __unicode__(self):
        return 'Bookmark %s has Tag[%s]' % (self.bookmark, self.tag)
