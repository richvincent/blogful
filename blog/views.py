from flask import render_template

from blog import app
from .database import session, Entry
from flask import request, redirect, url_for, abort
from flask import flash
from flask.ext.login import login_user
from werkzeug.security import check_password_hash
from .database import User

from flask.ext.login import login_required

from flask.ext.login import current_user

from flask.ext.login import logout_user


@app.route("/")
@app.route("/page/<int:page>", methods=["GET"])
def entries(page=1):

    try:
        PAGINATE_BY = int(request.args.get('limit'))

    except TypeError:
        PAGINATE_BY = 5

    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    if PAGINATE_BY > count:
        PAGINATE_BY = count

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) / PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
                           entries=entries,
                           has_next=has_next,
                           has_prev=has_prev,
                           page=page,
                           total_pages=total_pages,
                           limit=PAGINATE_BY
                           )


@app.route("/entry/<int:entryId>/")
def display_entry(entryId=1):

    entry = session.query(Entry).get(entryId)
    if entry is None:
        abort(404)
    return render_template("display_entry.html",
                           entry=entry)


@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")


@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    if entry is None:
        abort(404)
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/entry/<int:entryId>/edit/", methods=["GET"])
@login_required
def edit_entry_get(entryId=1):

    entry = session.query(Entry).get(entryId)
    if entry is None:
        abort(404)
    if entry.author_id != current_user.id:
        return render_template("not_authorized_edit.html")

    return render_template("edit_entry.html", entry=entry)


@app.route("/entry/<int:entryId>/edit/", methods=["POST"])
@login_required
def edit_entry_post(entryId=1):

    entry = session.query(Entry).get(entryId)
    if entry is None:
        abort(404)
    entry.title = request.form["title"]
    entry.content = request.form["content"]
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/entry/<int:entryId>/delete")
def delete_entry_get(entryId=1):

    entry = session.query(Entry).get(entryId)
    if entry is None:
        abort(404)
    return render_template("delete_entry.html", entry=entry)


@app.route("/delete/confirmed/<int:entryId>")
def delete_entry_confirmed(entryId=1):

    entry = session.query(Entry).get(entryId)
    if entry is None:
        abort(404)
    session.delete(entry)
    session.commit()

    return render_template("delete_confirmed.html")


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('entries'))
