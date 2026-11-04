"""S.A.G.E. caregiver dashboard (Flask app factory)."""

import os
import secrets

from flask import Flask, abort, g, jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException

from . import config, queries
from .queries import DatabaseNotReady

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def create_app(overrides=None):
    app = Flask(__name__, instance_path=str(config.instance_dir()))
    app.config.update(
        DATABASE=config.default_database(),
        SECRET_KEY=config.load_secret_key(),
        API_KEY=config.load_api_key(),
        TIMEZONE=os.environ.get("SAGE_TIMEZONE") or None,
        MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
        API_MAX_BYTES=64 * 1024,          # one live event is tiny; refuse anything larger
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_IDLE_MINUTES=config.idle_minutes(),
        LOGIN_MAX_FAILURES=5,             # wrong attempts allowed within the window...
        LOGIN_WINDOW_MINUTES=15,
        LOGIN_LOCK_MINUTES=5,             # ...before sign-in pauses for this long
        LIVE_CHECK_SECONDS=2.0,           # how often the live stream looks for changes
        LIVE_STREAM_SECONDS=300,          # each stream ends after this; the browser reconnects
        LIVE_RETRY_MS=3000,               # browser waits this long before reconnecting
        LIVE_POLL_MS=10000,               # fallback polling interval
    )
    if overrides:
        app.config.update(overrides)

    from . import auth, live
    from .api import bp as api_bp
    from .demo import bp as demo_bp
    from .views import bp as views_bp

    @app.before_request
    def _setup_check():
        if request.endpoint == "static":
            return None
        if not app.config.get("SECRET_KEY"):
            return _not_ready()
        get_db()  # raises DatabaseNotReady, handled below
        return None

    app.before_request(auth.load_user_and_require_login)

    @app.before_request
    def _csrf_protect():
        if request.method in ("POST", "PUT", "PATCH", "DELETE") and request.endpoint not in auth.CSRF_EXEMPT:
            sent = request.form.get("csrf_token", "") or request.headers.get("X-CSRF-Token", "")
            if not sent or not secrets.compare_digest(sent, session.get("csrf_token", "")):
                abort(400, description="This page had been open for a while, so for your safety "
                                       "we could not do that. Please go back, reload the page and try again.")

    @app.teardown_appcontext
    def _close_db(_exc):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    @app.context_processor
    def _template_globals():
        return {"csrf_token": csrf_token, "current_user": g.get("user")}

    @app.errorhandler(DatabaseNotReady)
    def _db_not_ready(_exc):
        return _not_ready()

    @app.errorhandler(HTTPException)
    def _http_error(exc):
        if _wants_json():
            return jsonify(error=exc.name, message=exc.description), exc.code
        return render_template("error.html", error=exc), exc.code

    app.register_blueprint(auth.bp)
    app.register_blueprint(live.bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(demo_bp)
    return app


def _wants_json():
    return request.path.startswith("/api/") or request.path.startswith("/live/")


def _not_ready():
    if _wants_json():
        return jsonify(error="Service Unavailable",
                       message="The dashboard has not been set up yet. Run: python dashboard/manage.py init-db"), 503
    return render_template("setup.html"), 503


def get_db():
    from flask import current_app
    if "db" not in g:
        g.db = queries.connect(current_app.config["DATABASE"])
    return g.db


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]
