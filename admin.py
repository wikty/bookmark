# encoding: utf-8
import datetime

from flask import request, redirect
from flask_peewee.admin import Admin, ModelAdmin, AdminPanel
from flask_peewee.filters import QueryFilter

from app import app, db
from auth import auth
from models import User, Bookmark, Tag, Relationship


class UserStatsPanel(AdminPanel):
    template_name = 'admin/user_stats.html'

    def get_context(self):
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)
        signups_this_week = User.select().where(User.join_date > last_week).count()
        bookmarks_this_week = Bookmark.select().where(Bookmark.created_date > last_week).count()
        return {
            'signups': signups_this_week,
            'bookmarks': bookmarks_this_week,
        }

class BookmarkAdmin(ModelAdmin):
    columns = ('url', 'created_date', 'image', )
    foreign_key_lookups = {'user': 'username'}
    filter_fields = ('url', 'created_date', 'image', 'user__username', )

class TagAdmin(ModelAdmin):
    columns = ('name', )

class RelationshipAdmin(ModelAdmin):
    columns = ('tag', 'bookmark', )
    foreign_key_lookups = {'tag': 'name', 'bookmark': 'url'}



admin = Admin(app, auth, branding='Bookmark后台')
auth.register_admin(admin)
admin.register(Relationship, RelationshipAdmin)
admin.register(Tag, TagAdmin)
admin.register(Bookmark, BookmarkAdmin)
admin.register_panel('统计数据', UserStatsPanel)