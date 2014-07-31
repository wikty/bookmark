# encoding: utf-8
import re
import datetime

from validate_email import validate_email

from flask import request, redirect, url_for, render_template, flash, abort, get_flashed_messages, Markup, send_file

from flask_peewee.utils import get_object_or_404, object_list
from peewee import *

from config import *
from app import app, db
from auth import auth
from models import User, Bookmark, Tag, Relationship

#@app.route('/favicon.ico')
#def favicon():
#    favicon_file = os.path.join(APP_ROOT, 'favicon.ico')
#    if os.path.isfile(favicon_file):
#        return send_file(favicon_file, mimetype='image/x-icon')

@app.route('/')
def index():
    user = auth.get_logged_in_user()
    if user:
        return redirect(url_for('bookmark'))
    else:
        # random pick 30 bookmarks, If Database is MySQL, please use fn.Rand()
        # fn come from, from peewee import *
        bookmarks = Bookmark.select(Bookmark, User.username).join(User).order_by(fn.Random()).limit(PERPAGE)
        return object_list('bookmark_list.html',
                            bookmarks,
                            'bookmarks',
                            paginate_by=PERPAGE)

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    error = {}

    if request.method == 'POST':
        if not request.form['username']:
            error['username'] = u'请填写用户名'
        if not request.form['email']:
            error['email'] = u'请填写邮箱'
        elif not validate_email(request.form['email']):
            # if you want to validate is avaiable
            # validate_email(request.form['email'], verify=True)
            error['email'] = u'请填写有效的邮箱'
        if not request.form['password']:
            error['password'] = u'请输入密码'
        elif request.form['password'] != request.form['passwordconfirm']:
            error['password'] = u'两次输入的密码不一致'
        
        if not error:
            try:
                user = User.select().where(User.username == request.form['username']).get()
                error['username'] = u'用户名已存在'
            except User.DoesNotExist:
                # In the function User.create() invoke inst.save()
                # So use User() not User.create()
                user = User(
                    username=request.form['username'],
                    email=request.form['email'],
                    join_date=datetime.datetime.now()
                )
                
                user.set_password(request.form['password'])
                user.save()

                flash(Markup(u'你已注册成功，现在<a href="' + url_for('auth.login') + u'">登录</a>'), 'success')
                # or directly make user to login
                # auth.login_user(user)
                # return redirect(url_for('bookmark'))

    return render_template('signup.html', error=error, form=request.form)

@app.route('/bookmark/')
@auth.login_required
def bookmark():
    user = auth.get_logged_in_user()
    # object_list automatically invoke PaginateQuery
    # capture request.args.get('page') to calucalte pagination
    bookmarks = user.Bookmarks
    return object_list('bookmark_list.html',
                        bookmarks,
                        'bookmarks',
                        paginate_by=PERPAGE,
                        user=user)


@app.route('/bookmark/add/', methods=['GET', 'POST'])
@auth.login_required
def bookmark_add():
    error = {}
    bookmark = {}
    user = auth.get_logged_in_user()
    if request.method == 'POST':
        if not request.form['url']:
            error['url'] = u'书签的网址不能为空'
        if not request.form['url'].startswith('http://') and not request.form['url'].startswith('https://'):
            request.form['url'] = ''.join(['http://', request.form['url']])
        if not error:
            try:
                bookmark = Bookmark.select().where(Bookmark.user == user,
                                        Bookmark.url == request.form['url']
                ).get()
            except Bookmark.DoesNotExist:
                try:
                    db.database.set_autocommit(False)
                    
                    bookmark = Bookmark.create(
                        user=user,
                        url=request.form['url'],
                        title=request.form['title']
                    )
                    bookmark.fetch_image()
                    bookmark.save()

                    tagnames = re.split('\s+', request.form['tags'].strip())
                    # marksure request.form['tags'] not a empty string
                    if tagnames[0]:
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
                    db.database.rollback()
                    flash(u'对不起，服务器太累了，刚罢工了一会儿', 'error')
                else:
                    try:
                        db.database.commit()
                    except Exception as e:
                        db.database.rollback()
                        flash(u'对不起，服务器太累了，刚罢工了一会儿', 'error')
                finally:
                    db.database.set_autocommit(True)

                if not get_flashed_messages():
                    flash(u'你已经成功添加一个书签', 'success')
                    return redirect(url_for('bookmark'))
            else:
                flash(Markup(u'书签已经存在，也许你想要<a href="' + url_for('bookmark_edit', id=bookmark.id) + u'">编辑</a>此书签'), 'info')
    
    return render_template('bookmark_add.html', error=error, form=request.form, user=user, bookmark=bookmark)

@app.route('/bookmark/edit/<int:id>/', methods=['GET', 'POST'])
@auth.login_required
def bookmark_edit(id):
    user = auth.get_logged_in_user()
    bookmark = {}
    try:
        bookmark = Bookmark.get(Bookmark.id == id)
        bookmark.tags = ' '.join([Tag.get(Tag.id == tagID).name for tagID in [tag.tag for tag in bookmark.Tags]])
    except Bookmark.DoesNotExist:
        flash(u'你要编辑的书签不存在', 'error')
        return redirect(url_for('page_404'))
    
    error = {}
    if request.method == 'POST':
        try:
            bookmark = Bookmark.get(Bookmark.id == request.form['id'])
        except Bookmark.DoesNotExist:
            flash(u'你要编辑的书签不存在', 'error')
            return redirect(url_for('page_404'))
        if not request.form['url']:
            error['url'] = u'书签的网址不能为空'
        if not error:
            try:
                db.database.set_autocommit(False)
                
                # before update image, should remove old version
                if bookmark.url != request.form['url']:
                    bookmark.destory_image()
                    bookmark.url = request.form['url']
                    bookmark.fetch_image()
                
                bookmark.title = request.form['title']
                bookmark.save()
                
                tagnames = re.split('\s+', request.form['tags'].strip())
                # marksure request.form['tags'] not a empty string
                if tagnames[0]:
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
                db.database.rollback()
                flash(u'对不起，服务器太累了，刚罢工了一会儿', 'error')
            else:
                try:
                    db.database.commit()
                except Exception as e:
                    db.database.rollback()
                    flash(u'对不起，服务器太累了，刚罢工了一会儿', 'error')
            finally:
                db.database.set_autocommit(True)

            if not get_flashed_messages():
                flash(u'你刚刚完成一个书签的编辑', 'success')
                return redirect(url_for('bookmark'))

    return render_template('bookmark_edit.html', error=error, form=request.form, bookmark=bookmark, user=user)

@app.route('/bookmark/remove/<int:id>/', methods=['GET', 'POST'])
@auth.login_required
def bookmark_remove(id):
    user = auth.get_logged_in_user()
    bookmark = {}
    try:
        bookmark = Bookmark.get(Bookmark.id == id)
    except Bookmark.DoesNotExist:
        flash(u'你要删除的书签不存在', 'error')
        return redirect(url_for('page_404'))
    
    if request.method == 'POST':
        with db.database.transaction():
            bookmark.destory_image()
            bookmark.delete_instance(recursive=True)
            flash(u'你刚刚删除了一个书签', 'success')
            return redirect(url_for('bookmark'))
    
    return render_template('bookmark_remove.html', bookmark=bookmark, user=user)

@app.route('/404/')
def page_404():
    return render_template('404.html')
