"""Server-rendered pages for the caregiver."""

from pathlib import PurePath

from flask import (Blueprint, abort, current_app, flash, g, redirect, render_template,
                   request, url_for)

from . import get_db, live, queries
from . import presenters as p
from .auth import admin_required, hash_password, normalise_username, safe_next, validate_new_user
from .sources import JsonFileSource, ingest

bp = Blueprint("views", __name__)

PAGE_SIZE = 25
RECENT_ON_OVERVIEW = 5


def _tz():
    return p.get_tz(current_app.config["TIMEZONE"])


def _patient_or_404(patient_id):
    row = queries.get_patient(get_db(), patient_id)
    if row is None:
        abort(404, description="We could not find that person. They may have been removed.")
    return row


def _live_context():
    """What the page needs to keep itself up to date."""
    return {"live": True, "revision": queries.get_revision(get_db()), "updated_at": p.clock_now(_tz())}


@bp.get("/")
def home():
    conn = get_db()
    patients = queries.list_patients(conn)
    if len(patients) == 1:
        return redirect(url_for("views.patient_overview", patient_id=patients[0]["id"]))
    tz = _tz()
    people = [{**p.present_patient(row),
               "status": p.present_status(queries.patient_summary(conn, row["id"]), tz)}
              for row in patients]
    summary = p.glance_everyone(people) if people else None
    return render_template("home.html", people=people, summary=summary, **_live_context())


@bp.get("/patients/<int:patient_id>")
def patient_overview(patient_id):
    conn = get_db()
    row = _patient_or_404(patient_id)
    tz = _tz()
    try:
        range_key = p.parse_trend_range(request.args.get("range"))
    except p.FilterError:
        abort(400, description="That time period is not one we know. Please choose one of the buttons on the page.")
    patient = p.present_patient(row)
    status = p.present_status(queries.patient_summary(conn, patient_id), tz)
    to_check = [p.present_event(e, row, tz)
                for e in queries.query_events(conn, patient_id, limit=10, open_only=True)]
    recent = [p.present_event(e, row, tz)
              for e in queries.query_events(conn, patient_id, limit=RECENT_ON_OVERVIEW)]
    trend_rows = queries.gait_trend(conn, patient_id, start=p.trend_start(range_key))
    chart = p.build_trend_chart(trend_rows, tz, range_key, patient["call_name"])
    return render_template(
        "patient.html", patient=patient, status=status, glance=p.glance(patient, status),
        to_check=to_check, recent=recent, chart=chart, range_key=range_key,
        range_labels=p.TREND_RANGE_LABELS, chart_w=p.CHART_W, chart_h=p.CHART_H,
        band_medium_y=p.BAND_MEDIUM_Y, band_high_y=p.BAND_HIGH_Y, levels=p.LEVELS,
        total_events=queries.count_events(conn, patient_id), **_live_context())


@bp.get("/patients/<int:patient_id>/events")
def patient_events(patient_id):
    conn = get_db()
    row = _patient_or_404(patient_id)
    tz = _tz()
    patient = p.present_patient(row)
    common = {"patient": patient, "type_labels": p.TYPE_FILTER_LABELS,
              "severity_labels": p.SEVERITY_LABELS, "levels": p.LEVELS,
              "total_events": queries.count_events(conn, patient_id), **_live_context()}
    try:
        filters, form = p.parse_filters(request.args, tz)
        page = p.parse_page(request.args.get("page"))
    except p.FilterError as exc:
        form = {k: request.args.get(k, "") for k in ("type", "severity", "from", "to")}
        return render_template("events.html", events=[], form=form, filter_error=_plain_filter_error(exc),
                               matched=0, page=1, pages=1, filtered=True, **common), 400
    matched = queries.count_events(conn, patient_id, **filters)
    pages = max(1, -(-matched // PAGE_SIZE))
    page = min(page, pages)
    events = [p.present_event(e, row, tz)
              for e in queries.query_events(conn, patient_id, limit=PAGE_SIZE,
                                            offset=(page - 1) * PAGE_SIZE, **filters)]
    return render_template("events.html", events=events, form=form, filter_error=None,
                           matched=matched, page=page, pages=pages, filtered=any(form.values()),
                           **common)


def _plain_filter_error(exc):
    text = str(exc)
    if "after the end date" in text:
        return "The “From” date is after the “To” date. Please swap them round."
    if "date" in text:
        return "One of the dates could not be understood. Please pick it again from the calendar."
    return "Those choices could not be understood. Please press “Show everything” and choose again."


# --- "I've checked" and undo -----------------------------------------------------------

def _event_and_patient(event_id):
    conn = get_db()
    event = queries.get_event(conn, event_id)
    if event is None:
        abort(404, description="We could not find that alert. It may have been removed.")
    return event, queries.get_patient(conn, event["patient_id"])


@bp.post("/events/<int:event_id>/check")
def check(event_id):
    event, patient = _event_and_patient(event_id)
    queries.check_event(get_db(), event_id, g.user["id"])
    live.notify()
    flash({"text": f"Thank you. This is now marked as checked on {p.call_name(patient)}.",
           "undo_event": event_id}, "success")
    return redirect(safe_next(request.form.get("next"))
                    or url_for("views.patient_overview", patient_id=event["patient_id"]))


@bp.post("/events/<int:event_id>/uncheck")
def uncheck(event_id):
    event, _ = _event_and_patient(event_id)
    queries.uncheck_event(get_db(), event_id)
    live.notify()
    flash("Done. It is back on the list of things to check.", "success")
    return redirect(safe_next(request.form.get("next"))
                    or url_for("views.patient_overview", patient_id=event["patient_id"]))


# --- help ------------------------------------------------------------------------------

@bp.get("/help")
def help_page():
    return render_template("help.html", levels=p.LEVELS)


# --- adding results (admins) --------------------------------------------------------------

def _recent_imports(conn):
    tz = _tz()
    # Show "results" rather than "file:results.json": no technical words on screen.
    return [{"source": PurePath(row["source"].removeprefix("file:")).stem,
             "when": p.when_label(row["imported_at"], tz),
             "by": row["imported_by_name"],
             "added": row["added"], "duplicates": row["duplicates"], "rejected": row["rejected"],
             "failed": row["error"] is not None and row["added"] == 0}
            for row in queries.recent_imports(conn)]


@bp.get("/import")
@admin_required
def import_page():
    conn = get_db()
    return render_template("import.html", result=None, imports=_recent_imports(conn))


@bp.post("/import")
@admin_required
def import_upload():
    conn = get_db()
    upload = request.files.get("file")
    status = 200
    result = None
    if upload is None or not upload.filename:
        flash("Please choose a file first, then press “Add these results”.", "error")
        status = 400
    else:
        result = ingest(conn, JsonFileSource(upload.read(), filename=upload.filename),
                        user_id=g.user["id"])
        if result.added:
            live.notify()
        if result.error and not result.added:
            status = 400
    return render_template("import.html", result=result, imports=_recent_imports(conn)), status


# --- who can sign in (admins) -------------------------------------------------------------

def _users_page(form=None, problems=None, status=200):
    conn = get_db()
    tz = _tz()
    users = [{"id": u["id"], "username": u["username"], "display_name": u["display_name"],
              "role": u["role"], "role_label": p.ROLE_LABELS[u["role"]],
              "last_login": p.when_label(u["last_login_at"], tz) if u["last_login_at"] else None,
              "is_me": u["id"] == g.user["id"]}
             for u in queries.list_users(conn)]
    return render_template("users.html", users=users, form=form or {}, problems=problems or [],
                           role_labels=p.ROLE_LABELS, role_help=p.ROLE_HELP), status


@bp.get("/users")
@admin_required
def users():
    return _users_page()


@bp.post("/users")
@admin_required
def add_user():
    conn = get_db()
    form = {"username": normalise_username(request.form.get("username")),
            "display_name": (request.form.get("display_name") or "").strip(),
            "role": request.form.get("role") or ""}
    password = request.form.get("password") or ""
    problems = validate_new_user(form["username"], form["display_name"], password, form["role"])
    if password != (request.form.get("password_again") or ""):
        problems.append("The two passwords are not the same. Please type them again.")
    if not problems and queries.get_user_by_username(conn, form["username"]):
        problems.append("Someone already has that username. Please choose another.")
    if problems:
        return _users_page(form, problems, 400)
    queries.create_user(conn, form["username"], form["display_name"], hash_password(password), form["role"])
    flash(f"{form['display_name']} can now sign in with the username “{form['username']}”.", "success")
    return redirect(url_for("views.users"))


@bp.post("/users/<int:user_id>/remove")
@admin_required
def remove_user(user_id):
    conn = get_db()
    user = queries.get_user(conn, user_id)
    if user is None:
        abort(404, description="We could not find that person. They may already have been removed.")
    if user_id == g.user["id"]:
        # Also guarantees at least one manager always remains.
        flash("You cannot remove yourself. Ask another manager to do it.", "error")
        return redirect(url_for("views.users"))
    queries.delete_user(conn, user_id)
    flash(f"{user['display_name']} can no longer sign in.", "success")
    return redirect(url_for("views.users"))
