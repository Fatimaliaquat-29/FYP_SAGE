"""Signing in and out, inactivity sign-out, and who may do what.

- Passwords are stored only as Werkzeug salted hashes; they are never
  logged or written anywhere else.
- A failed sign-in never says whether the name or the password was wrong.
- After LOGIN_MAX_FAILURES wrong attempts for one name within
  LOGIN_WINDOW_MINUTES, that name is paused for LOGIN_LOCK_MINUTES. The
  pause is keyed by the name typed, so it does not reveal real accounts.
- A session ends after SESSION_IDLE_MINUTES without the person doing
  anything. Background live updates do not count as doing something.
"""

import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from functools import wraps
from urllib.parse import urlsplit

from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from . import get_db, queries

bp = Blueprint("auth", __name__)

# Pages anyone may open without signing in.
PUBLIC_ENDPOINTS = {"auth.login", "static", "api.receive_events"}
# The pipeline endpoint uses its own API key instead of a sign-in cookie.
CSRF_EXEMPT = {"api.receive_events"}
# Background requests that must not keep a session alive.
LIVE_HEADER = "X-Live-Refresh"

USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,31}$")
MIN_PASSWORD_LENGTH = 8
# Checked against when the name is unknown, so both cases take the same time.
_DUMMY_HASH = generate_password_hash(secrets.token_hex(16))

FAILED_MESSAGE = "We couldn’t sign you in with those details. Please check them and try again."


def hash_password(password):
    return generate_password_hash(password)


def normalise_username(raw):
    return (raw or "").strip().lower()[:64]


def validate_new_user(username, display_name, password, role):
    """Return a list of plain-language problems (empty if all is fine)."""
    problems = []
    if not USERNAME_RE.match(username or ""):
        problems.append("The username should be 3 to 32 letters or numbers (dots, dashes and "
                        "underscores are fine), with no spaces.")
    if not (display_name or "").strip() or len(display_name.strip()) > 60:
        problems.append("Please give a name to show on screen (up to 60 letters).")
    if len(password or "") < MIN_PASSWORD_LENGTH:
        problems.append(f"The password should be at least {MIN_PASSWORD_LENGTH} characters long.")
    if role not in queries.ROLES:
        problems.append("Please choose what this person is allowed to do.")
    return problems


def _is_live_request():
    return request.headers.get(LIVE_HEADER) == "1" or request.path.startswith("/live/")


def _unauthorised(message, reason):
    if request.path.startswith("/api/") or _is_live_request():
        return jsonify(error="Unauthorized", message=message, reason=reason), 401
    flash(message, "info")
    target = request.full_path.rstrip("?") if request.method == "GET" else None
    return redirect(url_for("auth.login", next=target))


def load_user_and_require_login():
    """Runs before every request."""
    g.user = None
    if request.endpoint in PUBLIC_ENDPOINTS:
        return None
    user_id = session.get("user_id")
    if user_id is not None:
        last_seen = session.get("last_seen", 0)
        idle_limit = current_app.config["SESSION_IDLE_MINUTES"] * 60
        if time.time() - last_seen > idle_limit:
            session.clear()
            return _unauthorised("For your privacy, you were signed out after a while without use. "
                                 "Please sign in again.", "expired")
        user = queries.get_user(get_db(), user_id)
        if user is None:
            session.clear()
            return _unauthorised("Please sign in to continue.", "signed_out")
        g.user = user
        if not _is_live_request():
            session["last_seen"] = time.time()
        return None
    if request.endpoint is None:
        return None  # unknown address: let it show the friendly "not found" page
    return _unauthorised("Please sign in to continue.", "signed_out")


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None or g.user["role"] != "admin":
            abort(403, description="Only the person who manages this dashboard can do this. "
                                   "If you need it done, please ask them.")
        return view(*args, **kwargs)
    return wrapped


def safe_next(target):
    """Only follow redirects back into this site."""
    if not target:
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//"):
        return None
    if target.startswith("/login") or target.startswith("/logout"):
        return None
    return target


def _now():
    return datetime.now(timezone.utc)


def _locked(failure):
    if failure is None or not failure["locked_until"]:
        return False
    return queries.parse_utc_string(failure["locked_until"]) > _now()


def _register_failure(conn, username, failure):
    cfg = current_app.config
    now = _now()
    window = timedelta(minutes=cfg["LOGIN_WINDOW_MINUTES"])
    if failure is None or queries.parse_utc_string(failure["first_failed_at"]) < now - window:
        failures, first = 1, now
    else:
        failures, first = failure["failures"] + 1, queries.parse_utc_string(failure["first_failed_at"])
    locked_until = None
    if failures >= cfg["LOGIN_MAX_FAILURES"]:
        locked_until = queries.to_utc_string(now + timedelta(minutes=cfg["LOGIN_LOCK_MINUTES"]))
    queries.save_login_failure(conn, username, failures, queries.to_utc_string(first), locked_until)
    return locked_until is not None


def _lock_message():
    minutes = current_app.config["LOGIN_LOCK_MINUTES"]
    return (f"There have been too many tries. For safety, please wait {minutes} minutes "
            f"and then try again.")


@bp.route("/login", methods=["GET", "POST"])
def login():
    conn = get_db()
    if session.get("user_id") and request.method == "GET" and queries.get_user(conn, session["user_id"]):
        return redirect(url_for("views.home"))
    next_url = safe_next(request.values.get("next"))
    no_users = queries.count_users(conn) == 0
    if request.method == "GET":
        return render_template("login.html", error=None, next_url=next_url, username="",
                               no_users=no_users)

    username = normalise_username(request.form.get("username"))
    password = request.form.get("password") or ""
    if not username or not password:
        return render_template("login.html", error="Please enter your username and your password.",
                               next_url=next_url, username=username, no_users=no_users), 400

    failure = queries.get_login_failure(conn, username)
    if _locked(failure):
        return render_template("login.html", error=_lock_message(), next_url=next_url,
                               username=username, no_users=no_users), 429

    user = queries.get_user_by_username(conn, username)
    password_ok = check_password_hash(user["password_hash"] if user else _DUMMY_HASH, password)
    if user is None or not password_ok:
        now_locked = _register_failure(conn, username, failure)
        message = _lock_message() if now_locked else FAILED_MESSAGE
        return render_template("login.html", error=message, next_url=next_url,
                               username=username, no_users=no_users), 429 if now_locked else 401

    queries.clear_login_failures(conn, username)
    queries.record_login(conn, user["id"])
    session.clear()  # fresh session on sign-in
    session["user_id"] = user["id"]
    session["last_seen"] = time.time()
    session["csrf_token"] = secrets.token_urlsafe(32)
    flash(f"Welcome, {user['display_name']}.", "success")
    return redirect(next_url or url_for("views.home"))


@bp.post("/logout")
def logout():
    session.clear()
    flash("You have signed out. See you soon.", "success")
    return redirect(url_for("auth.login"))
