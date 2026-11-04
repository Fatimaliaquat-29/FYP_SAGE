"""JSON API.

- POST /api/events: for the SAGE pipeline (and the demo replay). Needs the
  API key in "Authorization: Bearer <key>" or "X-API-Key: <key>". No
  sign-in cookie is used or accepted in its place.
- Everything else is read-only and needs a signed-in user.
"""

import secrets

from flask import Blueprint, abort, current_app, jsonify, request

from . import get_db, live, queries
from . import presenters as p
from .sources import PipelineSource, ingest

bp = Blueprint("api", __name__, url_prefix="/api")

MAX_LIMIT = 500


def _tz():
    return p.get_tz(current_app.config["TIMEZONE"])


def _patient_or_404(patient_id):
    row = queries.get_patient(get_db(), patient_id)
    if row is None:
        abort(404, description=f"No patient with id {patient_id}.")
    return row


def _int_arg(name, default, minimum, maximum):
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        abort(400, description=f"\"{name}\" must be a whole number.")
    if not minimum <= value <= maximum:
        abort(400, description=f"\"{name}\" must be between {minimum} and {maximum}.")
    return value


def _sent_key():
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return request.headers.get("X-API-Key", "").strip()


@bp.post("/events")
def receive_events():
    expected = current_app.config.get("API_KEY")
    if not expected:
        return jsonify(error="Service Unavailable",
                       message="No API key is configured. Run: python dashboard/manage.py init-db"), 503
    sent = _sent_key()
    if not sent or not secrets.compare_digest(sent.encode("utf-8"), expected.encode("utf-8")):
        resp = jsonify(error="Unauthorized", message="A valid API key is required.")
        resp.headers["WWW-Authenticate"] = 'Bearer realm="sage"'
        return resp, 401

    limit = current_app.config["API_MAX_BYTES"]
    if request.content_length is not None and request.content_length > limit:
        abort(413, description=f"Payload larger than {limit} bytes.")
    if not request.mimetype == "application/json":
        abort(415, description="Send the event as application/json.")
    raw = request.stream.read(limit + 1)
    if len(raw) > limit:
        abort(413, description=f"Payload larger than {limit} bytes.")

    conn = get_db()
    result = ingest(conn, PipelineSource(raw))
    if result.added:
        live.notify()
    body = {"added": result.added, "duplicates": result.duplicates,
            "rejected": result.rejected,
            "problems": [{"where": pr.where, "message": pr.technical} for pr in result.problems]}
    stored_anything = (result.added or result.duplicates or result.patients_added
                       or result.patients_updated)
    if not stored_anything and (result.error or result.problems):
        status = 400 if result.error_kind == "unreadable" else 422
        return jsonify(error="Bad Request" if status == 400 else "Unprocessable Entity",
                       message=result.error or "No valid records.", **body), status
    status = 201 if result.added else 200
    return jsonify(body), status


@bp.get("/health")
def health():
    queries.get_revision(get_db())
    return jsonify(status="ok")


@bp.get("/patients")
def patients():
    conn = get_db()
    tz = _tz()
    return jsonify(patients=[
        {**p.present_patient(row), "status": p.present_status(queries.patient_summary(conn, row["id"]), tz)}
        for row in queries.list_patients(conn)
    ])


@bp.get("/patients/<int:patient_id>")
def patient(patient_id):
    row = _patient_or_404(patient_id)
    status = p.present_status(queries.patient_summary(get_db(), patient_id), _tz())
    return jsonify(patient={**p.present_patient(row), "status": status})


@bp.get("/patients/<int:patient_id>/events")
def events(patient_id):
    conn = get_db()
    row = _patient_or_404(patient_id)
    tz = _tz()
    try:
        filters, _ = p.parse_filters(request.args, tz)
    except p.FilterError as exc:
        abort(400, description=str(exc))
    limit = _int_arg("limit", 50, 1, MAX_LIMIT)
    offset = _int_arg("offset", 0, 0, 10**9)
    rows = queries.query_events(conn, patient_id, limit=limit, offset=offset, **filters)
    return jsonify(
        total=queries.count_events(conn, patient_id, **filters), limit=limit, offset=offset,
        events=[p.present_event(e, row, tz) for e in rows],
    )


@bp.get("/patients/<int:patient_id>/gait-trend")
def gait_trend(patient_id):
    _patient_or_404(patient_id)
    try:
        range_key = p.parse_trend_range(request.args.get("range"))
    except p.FilterError as exc:
        abort(400, description=str(exc))
    rows = queries.gait_trend(get_db(), patient_id, start=p.trend_start(range_key))
    return jsonify(range=range_key, points=[
        {"occurred_at": r["occurred_at"], "risk_score": r["risk_score"], "severity": r["severity"]}
        for r in rows
    ])
