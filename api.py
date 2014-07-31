from flask_peewee.rest import RestAPI, RestResource, UserAuthentication, AdminAuthentication, RestrictOwnerResource

from app import app
from auth import auth
from models import User, Bookmark, Tag, Relationship


user_auth = UserAuthentication(auth)
admin_auth = AdminAuthentication(auth)

# instantiate our api wrapper
api = RestAPI(app, default_auth=user_auth)


class UserResource(RestResource):
    exclude = ('password', 'email', 'admin', 'active', )


class BookmarkResource(RestrictOwnerResource):
    owner_field = 'user'
    include_resources = {'user': UserResource}

class TagResource(RestResource):
	owner_field = 'user'
	include_resources = {'user': UserResource}

class RelationshipResource(RestrictOwnerResource):
    owner_field = 'user'
    include_resources = {
        'bookmark': BookmarkResource,
        'tag': TagResource
    }
    paginate_by = None


# register our models so they are exposed via /api/<model>/
api.register(User, UserResource, auth=admin_auth)
api.register(Bookmark, BookmarkResource)
api.register(Tag, TagResource)
api.register(Relationship, RelationshipResource)
