from flask import render_template

from blog import app
from .database import session, Entry
from flask import request, redirect, url_for, abort

PAGINATE_BY = 5


@app.route("/")
@app.route("/page/<int:page>", methods=["GET"])
def entries(page=1):

    if request.method == "GET":
        try:
            PAGINATE_BY = int(request.args.get('limit'))
            limit = request.args.get('limit')

        except TypeError:
            PAGINATE_BY = 5

    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) / PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    try:
        return render_template("entries.html",
                               entries=entries,
                               has_next=has_next,
                               has_prev=has_prev,
                               page=page,
                               total_pages=total_pages,
                               limit=limit
                               )
    except UnboundLocalError:
                            return render_template("entries.html",
                                                   entries=entries,
                                                   has_next=has_next,
                                                   has_prev=has_prev,
                                                   page=page,
                                                   total_pages=total_pages,
                                                   )


@app.route("/entry/<int:entryId>/")
def display_entry(entryId=1):

    entry = session.query(Entry).get(entryId)
    if entry is None:
        abort(404)
    return render_template("display_entry.html",
                           entry=entry)


@app.route("/entry/add", methods=["GET"])
def add_entry_get():
    return render_template("add_entry.html")


@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    if entry is None:
        abort(404)
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/entry/<int:entryId>/edit/", methods=["GET"])
def edit_entry_get(entryId=1):

    entry = session.query(Entry).get(entryId)
    if entry is None:
        abort(404)

    return render_template("edit_entry.html", entry=entry)


@app.route("/entry/<int:entryId>/edit/", methods=["POST"])
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
