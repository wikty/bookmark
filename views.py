import re
import datetime

from validate_email import validate_email

from flask import request, redirect, url_for, render_template, flash, abort, get_flashed_messages

from flask_peewee.utils import get_object_or_404, object_list
from peewee import *

from app import app, db
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

@app.route('/')
def index():
    if auth.get_logged_in_user():
        return bookmark()
    else:
        bookmarks = Bookmark.select().order_by(fn.Random()).limit(PERPAGE)  # random pick 30 bookmarks
        return object_list('bookmark_list.html',
                            bookmarks,
                            'bookmarks',
                            paginate_by=PERPAGE)

@app.route('/bookmark/')
@app.login_required
def bookmark(username):
    user = auth.get_logged_in_user()
    # object_list automatically invoke PaginateQuery
    # capture request.args.get('page') to calucalte pagination
    bookmarks = user.Bookmarks
    return object_list('bookmark_list.html',
                        bookmarks,
                        'bookmarks',
                        paginate_by=PERPAGE)


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
                bookmark = Bookmark.select().where(Bookmark.user == user,
                                        Bookmark.url == request.form['url']
                ).get()
            except Bookmark.DoesNotExist:
                try:
                    db.set_autocommit(False)
                    
                    bookmark = Bookmark.create(
                        user=user,
                        url=request.form['url'],
                        title=request.form['title']
                    )
                    bookmark.fetch_image()
                    bookmark.save()

                    tagnames = re.split('\s+', request.form['tags'].strip())
                    for tagname in tagnames:
                        if not Tag.select().where(Tag.user == user,
                                                  Tag.name == tagname
                                                 ).exists():
                            tag = Tag.create(user=user, name=tagname)
                            tag.save()

                            relationship = Relationship.create(
                                user=user,
                                tag=tag,
                                bookmark=bookmark)
                            relationship.save()
                except Exception as e:
                    db.rollback()
                    flash('对不起，服务器太累了，刚罢工了一会儿', 'error')
                else:
                    try:
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        flash('对不起，服务器太累了，刚罢工了一会儿', 'error')
                finally:
                    db.set_autocommit(True)

                if not get_flashed_messages():
                    return redirect(url_for('bookmark'))
            else:
                flash('书签已经存在，也许你想要<a href="' + url_for('bookmark_edit', id=bookmark.id) + '">编辑</a>此书签', 'info')
    return render_template('bookmark_add.html', error=error)

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