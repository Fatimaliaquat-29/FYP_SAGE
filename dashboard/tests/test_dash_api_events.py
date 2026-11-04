"""POST /api/events: the endpoint the pipeline (and the demo replay) sends events to."""

import io
import json

import pytest

from conftest import API_KEY, ago, fall, gait, iso, make_app, patient
from sage_dashboard import queries


def post(client, body, key=API_KEY, header="bearer", content_type="application/json", raw=None):
    headers = {}
    if key is not None:
        headers = {"Authorization": f"Bearer {key}"} if header == "bearer" else {"X-API-Key": key}
    data = raw if raw is not None else json.dumps(body)
    return client.post("/api/events", data=data, headers=headers, content_type=content_type)


@pytest.fixture
def pipe(app, db_path):
    """A client with no sign-in cookie, and one known patient."""
    conn = queries.connect(db_path)
    queries.upsert_patient(conn, "P001", "Amina Rahman")
    conn.commit()
    conn.close()
    return app.test_client()


def stored(db_path):
    conn = queries.connect(db_path)
    rows = queries.query_events(conn, 1, limit=100)
    conn.close()
    return rows


@pytest.mark.parametrize("header", ["bearer", "x-api-key"])
def test_valid_key_stores_event(pipe, db_path, header):
    resp = post(pipe, fall(1, ago(minutes=1)), header=header)
    assert resp.status_code == 201
    assert resp.get_json() == {"added": 1, "duplicates": 0, "rejected": 0, "problems": []}
    rows = stored(db_path)
    assert len(rows) == 1 and rows[0]["source"] == "live" and rows[0]["import_id"] is None


def test_live_events_are_not_logged_as_imports(pipe, db_path):
    post(pipe, fall(1, ago(minutes=1)))
    conn = queries.connect(db_path)
    assert queries.recent_imports(conn) == []
    conn.close()


def test_event_raises_revision(pipe, db_path):
    conn = queries.connect(db_path)
    before = queries.get_revision(conn)
    conn.close()
    post(pipe, fall(1, ago(minutes=1)))
    conn = queries.connect(db_path)
    assert queries.get_revision(conn) > before
    conn.close()


@pytest.mark.parametrize("key", [None, "", "wrong-key", API_KEY + "x", API_KEY[:-1]])
def test_missing_or_wrong_key_rejected(pipe, db_path, key):
    resp = post(pipe, fall(1, ago(minutes=1)), key=key)
    assert resp.status_code == 401
    assert resp.get_json()["message"] == "A valid API key is required."
    assert "Bearer" in resp.headers["WWW-Authenticate"]
    assert stored(db_path) == []


def test_sign_in_cookie_is_not_enough(seeded, client, db_path):
    before = len(stored(db_path))
    resp = client.post("/api/events", data=json.dumps(fall(77, ago(minutes=1))),
                       content_type="application/json")
    assert resp.status_code == 401
    assert len(stored(db_path)) == before


def test_no_key_configured(db_path, user_ids):
    app = make_app(db_path, API_KEY=None)
    resp = post(app.test_client(), fall(1, ago(minutes=1)))
    assert resp.status_code == 503


def test_no_csrf_needed_with_key(pipe):
    assert post(pipe, fall(1, ago(minutes=1))).status_code == 201


@pytest.mark.parametrize("raw", [b"{not json", b"", b"\xff\xfe", b"{\"confidence\": NaN}"])
def test_malformed_payload(pipe, raw):
    resp = post(pipe, None, raw=raw)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Bad Request"


@pytest.mark.parametrize("raw", [b"[]", b"\"text\"", b"42"])
def test_wrong_shape(pipe, raw):
    assert post(pipe, None, raw=raw).status_code == 422


def test_wrong_content_type(pipe):
    resp = post(pipe, None, raw=json.dumps(fall(1, ago(minutes=1))), content_type="text/plain")
    assert resp.status_code == 415


@pytest.mark.parametrize("field", ["patient", "timestamp", "type", "confidence"])
def test_missing_fields(pipe, db_path, field):
    ev = fall(1, ago(minutes=1))
    del ev[field]
    resp = post(pipe, ev)
    assert resp.status_code == 422
    body = resp.get_json()
    assert body["added"] == 0 and body["problems"][0]["message"] == f"missing \"{field}\""
    assert stored(db_path) == []


@pytest.mark.parametrize("changes,fragment", [
    ({"type": "gait_risk"}, "missing \"risk_score\""),
    ({"confidence": 2}, "between 0 and 1"),
    ({"confidence": "high"}, "must be a number"),
    ({"type": "slip"}, "\"type\" must be one of"),
    ({"severity": "extreme"}, "\"severity\" must be one of"),
    ({"timestamp": "soon"}, "ISO 8601"),
    ({"patient": "P404"}, "unknown patient"),
    ({"details": "text"}, "\"details\" must be an object"),
    ({"event_id": "x" * 201}, "longer than 200"),
])
def test_every_field_is_validated(pipe, db_path, changes, fragment):
    resp = post(pipe, {**fall(1, ago(minutes=1)), **changes})
    assert resp.status_code == 422
    assert fragment in resp.get_json()["problems"][0]["message"]
    assert stored(db_path) == []


def test_duplicate_event(pipe, db_path):
    ev = fall(1, ago(minutes=1))
    assert post(pipe, ev).status_code == 201
    resp = post(pipe, ev)
    assert resp.status_code == 200 and resp.get_json()["duplicates"] == 1
    assert len(stored(db_path)) == 1


def test_batch_with_new_patient(app, db_path):
    client = app.test_client()
    body = {"format_version": 1, "patients": [patient("P9", "Yusuf Ali")],
            "events": [fall(1, ago(minutes=2), pid="P9"), gait(1, ago(minutes=1), 0.5, pid="P9"),
                       {"patient": "P9"}]}
    resp = post(client, body)
    assert resp.status_code == 201
    assert resp.get_json()["added"] == 2 and resp.get_json()["rejected"] == 1


def test_patients_only(app, db_path):
    resp = post(app.test_client(), {"patients": [patient("P5", "Zara")]})
    assert resp.status_code == 200
    conn = queries.connect(db_path)
    assert queries.get_patient_id_by_external(conn, "P5") is not None
    conn.close()


def test_very_large_payload_refused(pipe, db_path, app):
    big = {**fall(1, ago(minutes=1)), "description": "x" * (app.config["API_MAX_BYTES"] + 10)}
    resp = post(pipe, big)
    assert resp.status_code == 413
    assert stored(db_path) == []


def test_large_payload_without_length_header_refused(pipe, db_path, app):
    big = json.dumps({**fall(1, ago(minutes=1)), "description": "x" * (app.config["API_MAX_BYTES"] + 10)}).encode()
    # As a real server hands on a chunked upload: decoded, no Content-Length, input marked complete.
    resp = pipe.post("/api/events", input_stream=io.BytesIO(big),
                     headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json",
                              "Transfer-Encoding": "chunked"},
                     environ_overrides={"wsgi.input_terminated": True})
    assert resp.status_code == 413
    assert stored(db_path) == []


def test_get_not_allowed(pipe):
    resp = pipe.get("/api/events", headers={"Authorization": f"Bearer {API_KEY}"})
    assert resp.status_code == 405 and resp.is_json
