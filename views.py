import re
import datetime

from validate_email import validate_email

from flask import request, redirect, url_for, render_template, flash, abort

from flask_peewee.utils import get_object_or_404, object_list

from app import app
from auth import auth
from models import User, Bookmark, Tag, Relationship


#def homepage():
#    if auth.get_logged_in_user():
#        return private_timeline()
#    else:
#        return public_timeline()
@app.route('/private/')
@auth.login_required
def private_timeline():
    user = auth.get_logged_in_user()

    messages = Message.select().where(
        Message.user << user.following()
    ).order_by(Message.pub_date.desc())

    return object_list('private_messages.html', messages, 'message_list')

@app.route('/public/')
def public_timeline():
    messages = Message.select().order_by(Message.pub_date.desc())
    return object_list('public_messages.html', messages, 'message_list')

@app.route('/')
def index():
    if auth.get_logged_in_user():
        return bookmark()
    else:
        bookmarks = Bookmark.select().order_by(('created_date', 'desc')).limit(20)

@app.route('/bookmark/')
def bookmark():
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

    return object_list('bookmark_list.html', bookmarks, 'bookmarks', per_page=PERPAGE, total_pages=total_pages)

@app.route('/add/')
def add():
    password = request.args.get('password')
    if password != PASSWORD:
        abort(404)

    url = request.args.get('url')
    if url:
        bookmark = Bookmark(url=url)
        bookmark.fetch_image()
        bookmark.save()
        return redirect(url)
    abort(404)



@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    error = {}

    if request.method == 'POST':
        if not request.form['username']:
            error['username'] = '请填写用户名'
        if not request.form['email']:
            error['email'] = '请填写邮箱'
            return
        elif not validate_email(request.form['email'], verify=True):
            error['email'] = '请填写有效的邮箱'
            return
        if request.form['password'] != request.form['passwordconfirm']:
            error['password'] = '两次输入的密码不一致'

        if not error:
            try:
                user = User.select().where(User.username==request.form['username'].get()
                error['username'] = '用户名已存在'
            except User.DoesNotExist:
                user = User(
                    username=request.form['username'],
                    email=request.form['email'],
                    join_date=datetime.datetime.now()
                )
                user.set_password(request.form['password'])
                user.save()

                flash('你已注册成功，现在<a href="' + url_for('auth.login') + '">登录</a>', 'success')

                # auth.login_user(user)
                # return redirect(url_for('bookmark'))

    return render_template('signup.html', error=error, form=request.form)

@app.route('/following/')
@auth.login_required
def following():
    user = auth.get_logged_in_user()
    return object_list('user_following.html', user.following(), 'user_list')

@app.route('/followers/')
@auth.login_required
def followers():
    user = auth.get_logged_in_user()
    return object_list('user_followers.html', user.followers(), 'user_list')

@app.route('/users/')
def user_list():
    users = User.select().order_by(User.username)
    return object_list('user_list.html', users, 'user_list')

@app.route('/users/<username>/')
def user_detail(username):
    user = get_object_or_404(User, User.username==username)
    messages = user.message_set.order_by(Message.pub_date.desc())
    return object_list('user_detail.html', messages, 'message_list', person=user)

@app.route('/users/<username>/follow/', methods=['POST'])
@auth.login_required
def user_follow(username):
    user = get_object_or_404(User, User.username==username)
    Relationship.get_or_create(
        from_user=auth.get_logged_in_user(),
        to_user=user,
    )
    flash('You are now following %s' % user.username)
    return redirect(url_for('user_detail', username=user.username))

@app.route('/users/<username>/unfollow/', methods=['POST'])
@auth.login_required
def user_unfollow(username):
    user = get_object_or_404(User, User.username==username)
    Relationship.delete().where(
        Relationship.from_user==auth.get_logged_in_user(),
        Relationship.to_user==user,
    ).execute()
    flash('You are no longer following %s' % user.username)
    return redirect(url_for('user_detail', username=user.username))
# CREATE
# user = User.create(username='wikty', active=True)
# user.save()
# user.id
#
# q = User.insert(**{'username': 'admin'})  # insert one row
# usernames = ['wikty','mouse', 'moss']
# usernames = [{'username': user} for user in usernames]
# q = User.insert_many(usernames)  # insert multiple rows
# q.execute()
#
# UPDATE
# user = User.get(User.id==2)
# user.username = 'xiao'  # the user had a primary key
# user.save()  # update the instance
# 
# q = Food.update(price=Food.price + 12).where(Food.created_date < this_week)
# q.execute()  # update multiple records
#
# DELETE
# user = User.get(User.id==2)
# user.delete_instance()  # delete the instance
#
# q = User.delete().where(User.active=False)
# q.execute()
#
# RETIRVE
# user = User.get(username='wikty')  # just return one result, if no match, raise User.DoesNotExist
# 
# q = User.select()  # when you iterate the query, it will automatically execute
#
# the ForeignKeyField as a SelectQuery by related_name, e.g.
# for bookmark in user.Bookmarks  # iterate
# for bookmark in user.Bookmarks.order_by(Bookmark.created_date)  # iterate and append query
#
# specific filter
# where((User.username == 'wikty') |(User.username == 'mouse'))  # or condition
# users = User.select()where(fn.Lower(fn.Substr(User.username, 1, 1)) == 'a')  # database function
# bookmarks = Bookmark.select().where(Bookmark.user << users)  # item in set
# 
# sort
# User.select().order_by(User.username)
# User.select().order_by(User.username.desc())
# Bookmark.select().join(User).order_by(User.username, Bookmark.created_date.desc())
#
# random results
# PostgreSQL and SQLite
# bookmarks = Bookmark.select().order_by(fn.Random()).limit(5)  # pick 5 random bookmarks
# MySQL
# bookmarks = Bookmark.select().order_by(fn.Rand()).limit(5)  # pick 5 random bookmarks
#
# paginate
# Bookmark.select().order_by(Bookmark.created_date).paginate(2, 20)  # (pagenum, perpage), pagenum start as 1
# 
# count
# Bookmark.select().count()
# Bookmark.select(fn.Count(fn.Distinct(Bookmark.url))).scalar()  # return 30
# Employee.select(fn.Min(Employee.salary), fn.Max(Employee.salary)).scalar(as_tuple=True)  # return (200, 300)
#
# iterate large results
# for b in Bookmark.select().execute().iterator():
# for b in Bookmark.select().native.execute().iterator():
#
# alias 
# query = User.select(User, fn.Count(Tweet.id).alias('ct')).join(Tweet).group_by(User).order_by(SQL('ct'))
#
# group by
# q = User.select().annotate(Bookmark)  # is equivalent to the following
# q = User.select(User, fn.Count(Bookmark.id).alias('count')).join(Bookmark).group_by(User)
# q = User.select().join(Bookmark, JOIN_LEFT_OUTER).annotate(Bookmark)  # contain user even no bookmark
# q = User.select().annotate(Bookmark, fn.Max(Bookmark.created_date).alias('latest'))
# q = Tag.select().join(Bookmark2Tag).join(Bookmark).group_by(Tag).having(fn.Count(Bookmark.id) > 5)
# q = Tag.select(Tag, fn.Count(Bookmark.id).alias('count')).join(Bookmark2Tag).join(Bookmark).group_by(Tag).having(fn.Count(Bookmark.id) > 5)
# 
# one -> multiple
# Message.select().join(User).where(User.username == 'wikty')
# User.select().join(Message).where(User.username == 'wikty')
# 
# multiple -> mutiple
# Tag.select().join(Bookmark2Tag).join(Bookmark)




@app.route('/bookmark/add/', methods=['GET', 'POST'])
@auth.login_required
def bookmark_add():
    error = {}
    user = auth.get_logged_in_user()
    if request.method == 'POST':
        if not request.form['url']:
            error['url'] = '书签的网址不能为空'

        if not error:
            try:
                Bookmark.select().where(Bookmark.user == user,
                                        Bookmark.url == request.form['url']
                ).get()
            except Bookmark.DoesNotExist:
                bookmark = Bookmark.create(
                    user=user,
                    url=request.form['url'],
                    title=request.form['title']
                )
                bookmark.fetch_image()
                bookmark.save()

                tags = re.split('\s+', request.form['tags'].strip())
                if not Tag.select().where(Tag.user==user,
                                          )







        message = Message.create(
            user=user,
            content=request.form['content'],
        )
        flash('Your message has been created')
        return redirect(url_for('user_detail', username=user.username))

    return render_template('bookmark_add.html')

@app.route('/bookmark/edit/<int:id>/', methods=['GET', 'POST'])
@auth.login_required
def bookmark_edit(id):
    user = auth.get_logged_in_user()
    message = get_object_or_404(Message, Message.user==user, Message.id==message_id)
    if request.method == 'POST' and request.form['content']:
        message.content = request.form['content']
        message.save()
        flash('Your changes were saved')
        return redirect(url_for('user_detail', username=user.username))

    return render_template('bookmark_edit.html', message=message)

@app.route('/bookmark/remove/<int:id>/', methods=['GET', 'POST'])
@auth.login_required
def bookmark_remove(id):
    return render_template('bookmark_remove.html')