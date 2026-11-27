"""User Manager: a small Flask + MySQL CRUD demo for a database systems course."""
import csv
import io
import os
import secrets

from dotenv import load_dotenv
from flask import (Flask, Response, abort, flash, redirect, render_template,
                   request, session, url_for)
from mysql.connector import Error, errorcode, pooling

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")


# One pool for the whole app: connections are expensive, so reuse them.
pool = pooling.MySQLConnectionPool(
    pool_name="webpool",
    pool_size=5,
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", 3306)),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.environ["DB_NAME"],
)

# Identifiers cannot be parameterized, so we whitelist sortable columns.
SORTABLE = {"user_id" : "user_id", "name" : "username",
                "email" : "email", "joined" : "date_joined", 
                "album_name" : "album_name", "artist_name" : "artist_name"}


# ---------- database helper ----------
def run(sql, params=(), *, fetch=False, commit=False):
    """Run ONE parameterized statement and always give the connection back."""
    conn = pool.get_connection()
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if commit:
            conn.commit()
        return cur.fetchall() if fetch else cur.rowcount
    except Error:
        conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        conn.close()  # returns the connection to the pool


# ---------- CSRF protection (state-changing requests only) ----------
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def verify_csrf():
    if request.method == "POST":
        sent = request.form.get("_csrf", "")
        if not secrets.compare_digest(sent, session.get("_csrf", "")):
            abort(400, "Invalid CSRF token")


# ---------- validation ----------
def read_form(form):
    data = {
        "username": form.get("username", "").strip(),
        "email": form.get("email", "").strip().lower(),
    }
    errors = []
    if not data["username"] or len(data["username"]) > 50:
        errors.append("Name is required (max 50 characters).")
    if "@" not in data["email"] or len(data["email"]) > 50:
        errors.append("A valid email is required.")
    return data, errors

def read_album_form(form):
    data = {
        "album_name" : form.get("album_name", "").strip(),
        "artist_id" : form.get("artist_id", "").strip(),
        "release_date" : form.get("release_date", "").strip(),
        "cover_image_url" : form.get("cover_image_url").strip()
    }

    errors = []

    if len(data["album_name"]) > 50:
        errors.append("Album name is too long (max 50 characters).")

    return data, errors

def read_edit_album_form(form):
    data = {
        "album_name" : form.get("album_name", "").strip(),
        "artist_id" : form.get("artist_id", "").strip(),
        "release_date" : form.get("release_date", "").strip(),
        "cover_image_url" : form.get("cover_image_url").strip()
    }

    errors = []

    if len(data["album_name"]) > 50:
        errors.append("Album name is too long (max 50 characters).")

    errors = []

    if len(data["cover_image_url"]) > 2048:
        errors.append("Cover image url is too long (2048 characters).")

    return data, errors
        
def read_artist_form(form):
    data = {
        "artist_name" : form.get("artist_name", "").strip()
    }

    errors = []

    if not data["artist_name"] or len(data["artist_name"]) > 50:
        errors.append("Artist name required (50 characters max).")

    return data, errors

def read_rating_form(form):
    data = {
        "user_id" : form.get("user_id", "").strip(),
        "album_id" : form.get("album_id", "").strip(),
        "album_rating" : form.get("album_rating", "").strip()
    }

    errors = []

    if not data["album_rating"] or not (0.0 < float(data["album_rating"])  < 10.0):
        errors.append("Album rating required (0.0 - 10.0).")

    return data, errors

def read_song_rating_form(form):
    data = {
        "user_id" : form.get("user_id", "").strip(),
        "album_id" : form.get("album_id", "").strip(),
        "song_id" : form.get("song_id", "").strip(),
        "song_rating" : form.get("song_rating", "").strip()
    }

    errors = []

    if not data["user_id"]:
        errors.append("User Required")
    if not data["album_id"]:
        errors.append("Album Required")
    if not data["song_id"]: 
        errors.append("Song Required")
    if not data["song_rating"] or not (0.0 < float(data["song_rating"]) < 10.0):
        errors.append("Song rating required (0.0 - 10.0).")

    return data, errors

def db_error_message(e):
    if e.errno == errorcode.ER_DUP_ENTRY:
        return "That email is already registered."
    app.logger.exception("Database error")  # details go to the log, not the user
    return "A database error occurred. Please try again."


# ---------- READ: list + search + sort ----------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "user_id")
    column = SORTABLE.get(sort, "user_id")
    users = run(
        f"SELECT * FROM users WHERE username LIKE %s OR email LIKE %s "
        f"ORDER BY {column}",           # column comes from our whitelist, not the user
        (f"%{q}%", f"%{q}%"), fetch=True)

    ratings = run("SELECT ar.user_id, album_name, rating, created_at "
                  "FROM album_ratings ar join albums a "
                  "ON ar.album_id = a.album_id "
                  "ORDER BY album_name ASC", fetch=True)

    for user in users:
        user["ratings"] = [
            rating for rating in ratings if rating["user_id"] == user["user_id"]
        ]
    return render_template("index.html", users=users, q=q, sort=sort)

# ------------- Album List -------------
@app.route("/albums")
def albums():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "album_id")
    column = SORTABLE.get(sort, "album_id")
    albums_data = run(f"SELECT a.album_id, a.album_name, artist_name, a.release_date, a.cover_image_url, round(avg(rating), 2) as avg_rating, count(rating_id) as num_ratings "
                 f"FROM albums a JOIN artists "
                 f"ON a.artist_id = artists.artist_id "
                 f"LEFT JOIN album_ratings ar ON a.album_id = ar.album_id "
                 f"WHERE a.album_name LIKE %s OR artist_name LIKE %s "
                 f"GROUP BY a.album_id "
                 f"ORDER BY {column}", (f"%{q}%", f"%{q}%"),fetch = True)

    songs = run("SELECT album_id, song_name, track_number FROM songs "
                "ORDER BY album_id, track_number", fetch=True)

    for album in albums_data:
        album["songs"] = [
            song for song in songs if song["album_id"] == album["album_id"]
        ]
    return render_template("albums.html", albums = albums_data, q=q, sort=sort)

# ------------- Artist List -------------
@app.route("/artists")
def artists():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "artist_id")
    column = SORTABLE.get(sort, "artist_id")
    artists = run(f"SELECT artists.artist_id, artist_name, max(release_date) as most_recent_release FROM artists "
                  f"LEFT JOIN albums ON artists.artist_id = albums.artist_id "
                  f"GROUP BY artist_id "
                  f"HAVING artist_name LIKE %s", (f"%{q}%",),fetch=True)
    return render_template("artists.html", artists=artists, q=q, sort=sort)

# --------------- songs list ----------------
@app.route("/songs")
def songs():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "song_id")
    column = SORTABLE.get(sort, "song_id")
    songs = run(f"SELECT s.song_name, album_name, artist_name, release_date, round(avg(sr.rating), 2) as avg_rating, "
                f"duration_seconds, cover_image_url, count(rating_id) as num_ratings FROM songs s "
                f"JOIN albums a ON s.album_id = a.album_id "
                f"JOIN artists ar ON a.artist_id = ar.artist_id "
                f"LEFT JOIN song_ratings sr ON s.song_id = sr.song_id "
                f"GROUP BY s.song_id "
                f"HAVING song_name LIKE %s OR artist_name LIKE %s OR album_name LIKE %s", (f"%{q}%", f"%{q}%", f"%{q}%"), fetch=True)
    return render_template("songs.html", songs=songs, q=q, sort=sort)

# -------------- top music list ------------
@app.route("/top-music")
def top_music():
    albums = run("SELECT a.album_id, a.album_name, round(avg(rating), 2) as avg_rating, a.cover_image_url, count(rating_id) as num_ratings, artist_name FROM albums a "
                 "JOIN album_ratings ar ON a.album_id = ar.album_id "
                 "JOIN artists ON a.artist_id = artists.artist_id "
                 "GROUP BY album_id "
                 "ORDER BY avg_rating DESC LIMIT 10", fetch=True)

    songs = run("SELECT s.song_name, a.album_name, round(avg(sr.rating), 2) as avg_rating, a.cover_image_url, "
                "count(sr.rating_id) as num_ratings, ar.artist_name FROM songs s "
                "JOIN song_ratings sr ON s.song_id = sr.song_id "
                "JOIN albums a ON s.album_id = a.album_id "
                "JOIN artists ar ON ar.artist_id = a.artist_id "
                "GROUP BY s.song_id "
                "ORDER BY avg_rating DESC LIMIT 10", fetch=True)
    return render_template("top_music.html", albums=albums, songs=songs)

# ---------- CREATE ----------
@app.route("/users/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        data, errors = read_form(request.form)
        if not errors:
            try:
                run("INSERT INTO users (username, email, date_joined) "
                    "VALUES (%(username)s, %(email)s, NOW())",
                    data, commit=True)
                flash("User added.", "ok")
                return redirect(url_for("index"))
            except Error as e:
                errors.append(db_error_message(e))
        for err in errors:
            flash(err, "error")
        return render_template("form.html", user=data, mode="Add")
    return render_template("form.html",
                           user={"username" : "", "email" : ""}, mode="Add")

# ---------- ADD ALBUM -----------
@app.route("/albums/new", methods=["GET", "POST"])
def add_album():
    artists = run("SELECT * FROM artists ORDER BY artist_name", fetch=True)
    if request.method == "POST":
        data, errors = read_album_form(request.form)
        if not errors:
            try:
                run("INSERT INTO albums (album_name, artist_id, release_date, cover_image_url) "
                    "VALUES (%(album_name)s, %(artist_id)s, %(release_date)s, %(cover_image_url)s)", data,
                    commit = True)
                flash("Album added.", "ok")
                return redirect(url_for("albums"))
            except Error as e:
                errors.append(db_error_message(e))
        for error in errors:
            flash(error, "error")
        return render_template("album_form.html", album = data, mode = "Add", artists=artists)
    return render_template("album_form.html",
                           album = {"album_name" : "", "artist_id" : "", "release_date" : "", "cover_image_url" : ""},
                           mode = "Add", artists=artists)

# ---------- ADD ARTIST ------------
@app.route("/artists/new", methods=["GET", "POST"])
def add_artist():
    if request.method == "POST":
        data, errors = read_artist_form(request.form)
        if not errors:
            try:
                run("INSERT INTO artists (artist_name) VALUES (%(artist_name)s)", data, commit=True)
                flash("Artist added.", "ok")
                return redirect(url_for("artists"))
            except Error as e:
                errors.append(db_error_message(e))
        for error in errors:
            flash(error, "error")
        return render_template("artist_form.html", artist=data, mode="Add")
    return render_template("artist_form.html", artist="", mode="Add")

# --------- ADD RATING ----------
@app.route("/ratings/new-album", methods=["GET", "POST"])
def add_album_rating():
    albums = run("SELECT album_id, album_name, artist_name FROM albums "
                 "JOIN artists ON albums.artist_id = artists.artist_id "
                 "ORDER BY album_name", fetch=True)
    users = run("SELECT user_id, username FROM users ORDER BY username", fetch=True)
    songs = run("SELECT song_id, album_id, song_name FROM songs "
                "ORDER BY track_number", fetch=True)
    if request.method == "POST":
        data, errors = read_rating_form(request.form)
        if not errors:
            try:
                run("INSERT INTO album_ratings (album_id, user_id, rating, created_at) "
                    "VALUES (%(album_id)s, %(user_id)s, %(album_rating)s, NOW())", data, commit=True)
                flash("Rating added.", "ok")
                return redirect(url_for('albums'))
            except Error as e:
                errors.append(db_error_message(e))
        for error in errors:
            flash(error, "error")
        return render_template("add_rating.html", albums=albums, users=users, rating=data, songs=songs)
    return render_template("add_rating.html", albums=albums, users=users, songs=songs,
                           rating={"user_id" : "", "album_id" : "", "album_rating" : ""})

@app.route("/ratings/new-song", methods=["GET", "POST"])
def add_song_rating():
    albums = run("SELECT album_id, album_name, artist_name FROM albums "
                 "JOIN artists ON albums.artist_id = artists.artist_id "
                 "ORDER BY album_name", fetch=True)
    users = run("SELECT user_id, username FROM users ORDER BY username", fetch=True)
    songs = run("SELECT song_id, album_id, song_name FROM songs "
                "ORDER BY track_number", fetch=True)    
    if request.method == "POST":
        data, errors = read_song_rating_form(request.form)
        if not errors:
            try:
                run("INSERT INTO song_ratings (song_id, user_id, rating, created_at) "
                    "VALUES (%(song_id)s, %(user_id)s, %(song_rating)s, NOW())", data, commit=True)
                flash("Rating added.", "ok")
                return redirect(url_for('index'))
            except Error as e:
                errors.append(db_error_message(e))
        for error in errors:
            flash(error, "error")
        return render_template("add_rating.html", albums=albums, users=users, rating=data, songs=songs)
    return render_template("add_rating.html", albums=albums, users=users, songs=songs,
                           rating={"user_id" : "", "album_id" : "", "song_id" : "", "song_rating" : ""})


# ---------- UPDATE ----------
@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit(user_id):
    rows = run("SELECT * FROM users WHERE user_id = %s", (user_id,), fetch=True)
    if not rows:
        abort(404)
    if request.method == "POST":
        data, errors = read_form(request.form)
        data["user_id"] = user_id
        if not errors:
            try:
                run("UPDATE users SET username=%(username)s, email=%(email)s "
                    "WHERE user_id=%(user_id)s", data, commit=True)
                flash("User updated.", "ok")
                return redirect(url_for("index"))
            except Error as e:
                errors.append(db_error_message(e))
        for err in errors:
            flash(err, "error")
        return render_template("form.html", user=data, mode="Edit")
    return render_template("form.html", user=rows[0], mode="Edit")

# ------------- edit album ---------------
@app.route("/album/<int:album_id>/edit", methods = ["GET", "POST"])
def edit_album(album_id):
    rows = run("SELECT * FROM albums WHERE album_id = %s", (album_id,), fetch=True)
    if not rows: abort(404)
    album = rows[0]
    artists = run("SELECT artist_id, artist_name FROM artists ORDER BY artist_name", fetch=True)
    if request.method == "POST":
        data, errors = read_edit_album_form(request.form)
        data["album_id"] = album_id
        if not errors:
            try:
                if data["album_name"]:
                    run("UPDATE albums SET album_name = %(album_name)s WHERE album_id = %(album_id)s", data, commit=True)
                if data["artist_id"]:
                    run("UPDATE albums SET artist_id = %(artist_id)s WHERE album_id = %(album_id)s", data, commit=True)
                if data["release_date"]:
                    run("UPDATE albums SET release_date = %(release_date)s WHERE album_id = %(album_id)s", data, commit=True)
                if data["cover_image_url"]:
                    run("UPDATE albums SET cover_image_url = %(cover_image_url)s WHERE album_id = %(album_id)s" , data, commit=True)
                flash("Album  updated.", "ok")
                return redirect(url_for("albums"))
            except Error as e:
                errors.append(db_error_message(e))
        for error in errors:
            flash(error, "error")
        return render_template("album_form.html", album=data, mode = "Edit", artists=artists)
    return render_template("album_form.html", album=album, mode = "Edit", artists=artists)

# ---------- DELETE (POST only: GET must never change data) ----------
@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete(user_id):
    removed = run("DELETE FROM users WHERE user_id = %s", (user_id,), commit=True)
    flash("User removed." if removed else "User not found.",
          "ok" if removed else "error")
    return redirect(url_for("index"))


# ---------- REPORT ----------
@app.route("/report")
def report():
    totals = run("SELECT COUNT(*) AS total "
                 "FROM users", fetch=True)[0]
    recent = run("SELECT username, email, date_joined FROM users "
                 "ORDER BY date_joined DESC, user_id DESC LIMIT 5", fetch=True)
    sql_report_data = run("SELECT * FROM users ORDER BY user_id", fetch=True)
    
    return render_template("report.html", totals=totals, recent=recent,
                            sql_report_data=sql_report_data)


@app.route("/report.csv")
def report_csv():
    rows = run("SELECT user_id, username, email, date_joined "
               "FROM users ORDER BY user_id", fetch=True)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["user_id", "username", "email", "date_joined"])
    for r in rows:
        writer.writerow(r.values())
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=users.csv"})


# ---------- connection check (handy in class) ----------
@app.route("/health")
def health():
    try:
        run("SELECT 1", fetch=True)
        return {"database": "ok"}
    except Error:
        return {"database": "unreachable"}, 503


if __name__ == "__main__":
    app.run(debug=True)
