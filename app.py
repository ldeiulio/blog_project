from flask import render_template, abort, request, url_for, flash, redirect, g
from create_app import app
from database import Entry, create_all, db_session, User, Base
from math import ceil
from flask_login import login_required, current_user
import login

create_all()

DEFAULT_NUM_PER_PAGE = 10


# allows for logged in users to create a new entry on blog
# creates a new Entry Objects and commits to database
# redirects to index upon successful entry
@app.route('/entry/add', methods=('GET', 'POST'))
@login_required
def create_entry():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']

        if not title:
            flash("Title is required")
        else:
            add_entry(title, body, current_user.id)
            return redirect('/')

    return render_template("new_post.html", authenticated=current_user.is_authenticated)


def add_entry(title, body, user_id):
    entry = Entry(title, body, user_id)
    db_session.add(entry)
    db_session.commit()


# is index page, renders entries made to blog in reverse chronological order
# if limit is defined in GET, and is a digit greater than 0, changes number of entries per page to limit
# if limit is greater than 100, defaults to DEFAULT_NUM_PER_PAGE
# if logged in user created a given entry, edit and delete hyperlinks will be displayed
@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def display_entries(page):
    entries = db_session.query(Entry, User.name).outerjoin(User, Entry.user_id == User.id).order_by(Entry.datetime.desc()).all()
    if request.method == "GET" and request.args.get("limit") is not None:
        if request.args.get("limit").isdigit() and int(request.args.get("limit")) > 0:
            g.num_per_page = int(request.args.get("limit"))
        else:
            g.num_per_page = DEFAULT_NUM_PER_PAGE
    else:
        g.num_per_page = DEFAULT_NUM_PER_PAGE
    g.total_pages = ceil(len(entries)/g.num_per_page)

    if (page > g.total_pages and page != 1) or page <= 0:
        abort(404)

    start = (page - 1) * g.num_per_page
    end = page * g.num_per_page
    return render_template("entries.html", entries=entries[start:end], has_next=has_next(page), has_prev=has_prev(page),
                           next_page=page_url(page+1), prev_page=page_url(page-1),
                           authenticated=current_user.is_authenticated, user_id=current_user.get_id())


# displays Entry with id entry_id
# if logged in user created a given entry, edit and delete hyperlinks will be displayed
@app.route('/entry/<int:entry_id>')
def display_entry(entry_id):
    entry = db_session.query(Entry, User.name).outerjoin(User, Entry.user_id == User.id).filter(Entry.id == entry_id).first()
    if entry is None:
        abort(404)
    return render_template("entry.html", entry=entry, authenticated=current_user.is_authenticated,
                           user_id=current_user.get_id())


# allows a logged in user to edit entry if he has matching id to user_id of entry
@app.route('/entry/<int:entry_id>/edit', methods=('GET', 'POST'))
@login_required
def edit_entry(entry_id):
    entry = db_session.query(Entry).filter(Entry.id == entry_id).first()
    if entry is None:
        abort(404)
    if int(current_user.get_id()) != entry.user_id:
        flash("you do not have permission to edit this entry")
        return redirect('/')
    if request.method == "POST":
        title = request.form['title']

        if not title:
            flash("Title is required")
        else:
            print(entry.content)
            entry.title = request.form['title']
            entry.content = request.form['body']
            db_session.commit()
            return redirect('/')
    return render_template("edit_post.html", entry=entry, authenticated=current_user.is_authenticated)


# allows a logged in user to delete entry if he has matching id to user_id of entry
@app.route('/entry/<int:entry_id>/delete', methods=('GET', 'Post'))
@login_required
def delete_entry(entry_id):
    entry = db_session.query(Entry).filter(Entry.id == entry_id).first()
    if entry is None:
        abort(404)
    if int(current_user.get_id()) != entry.user_id:
        flash("you do not have permission to edit this entry")
        return redirect('/')
    if request.method == "POST":
        confirm = request.form['confirm']
        if confirm == "confirm":
            db_session.delete(entry)
            db_session.commit()
            flash("entry deleted")
        return redirect('/')
    return render_template("delete_post.html", authenticated=current_user.is_authenticated)


# determines if there is a next page of entries exists given current page
def has_next(page):
    return page < g.total_pages


# return url to supplied page number
# used as helper to display_entries
def page_url(page):
    args = request.view_args.copy()
    args['page'] = page
    if request.args.get('limit') is not None:
        args['limit'] = request.args.get('limit')
    return url_for(request.endpoint, **args)


# determines if there is a previous page of entries exists given current page
def has_prev(page):
    return page > 1


if __name__ == '__main__':
    app.run()
