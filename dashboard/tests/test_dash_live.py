"""Live update endpoints (without a browser), the setup message, and the setup commands."""

import json
import sqlite3
import threading
import time

import pytest

import demo_replay
import manage
from conftest import API_KEY, CSRF, SAMPLE_FILE, ago, fall, make_app, sign_in
from sage_dashboard import config, create_app, queries
from sage_dashboard.live import notifier


def test_revision_endpoint(seeded, client):
    data = client.get("/live/revision").get_json()
    assert isinstance(data["revision"], int) and data["time"]


def test_revision_changes_after_event_and_check(seeded, client, db_path):
    first = client.get("/live/revision").get_json()["revision"]
    client.post("/api/events", data=json.dumps(fall(50, ago(minutes=1))),
                headers={"Authorization": f"Bearer {API_KEY}"}, content_type="application/json")
    second = client.get("/live/revision").get_json()["revision"]
    assert second > first
    client.post("/events/1/check", data={"csrf_token": CSRF})
    assert client.get("/live/revision").get_json()["revision"] > second


def read_events(resp, count, timeout=10):
    """Collect `count` SSE messages (event name, data) from a streamed response."""
    found, buffer = [], ""
    deadline = time.time() + timeout
    for chunk in resp.response:
        buffer += chunk.decode() if isinstance(chunk, bytes) else chunk
        while "\n\n" in buffer:
            block, buffer = buffer.split("\n\n", 1)
            lines = dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)
            if "event" in lines:
                found.append((lines["event"], json.loads(lines["data"])))
        if len(found) >= count or time.time() > deadline:
            break
    return found


def test_stream_sends_current_revision_then_changes(db_path, user_ids):
    app = make_app(db_path, LIVE_CHECK_SECONDS=0.2, LIVE_STREAM_SECONDS=10)
    client = sign_in(app.test_client(), user_ids["admin"])
    resp = client.get("/live/stream", buffered=False)
    assert resp.status_code == 200 and resp.mimetype == "text/event-stream"
    assert resp.headers["Cache-Control"] == "no-cache"

    def post_later():
        time.sleep(0.5)
        poster = app.test_client()
        conn = queries.connect(db_path)
        queries.upsert_patient(conn, "P001", "Amina Rahman")
        conn.commit()
        conn.close()
        poster.post("/api/events", data=json.dumps(fall(1, ago(minutes=1))),
                    headers={"Authorization": f"Bearer {API_KEY}"}, content_type="application/json")

    threading.Thread(target=post_later, daemon=True).start()
    events = read_events(resp, 3)
    resp.close()
    assert [name for name, _ in events][:1] == ["update"]
    revisions = [data["revision"] for name, data in events if name == "update"]
    assert len(revisions) >= 2 and revisions[-1] > revisions[0]


def test_stream_sees_changes_from_another_program(db_path, user_ids):
    """A write that bypasses this app (another process) is still noticed."""
    app = make_app(db_path, LIVE_CHECK_SECONDS=0.2, LIVE_STREAM_SECONDS=10)
    client = sign_in(app.test_client(), user_ids["admin"])
    resp = client.get("/live/stream", buffered=False)

    def write_directly():
        time.sleep(0.5)
        conn = queries.connect(db_path)
        queries.upsert_patient(conn, "P7", "Someone Else")
        conn.commit()
        conn.close()

    threading.Thread(target=write_directly, daemon=True).start()
    events = read_events(resp, 2)
    resp.close()
    assert len([e for e in events if e[0] == "update"]) == 2


def test_stream_ends_after_its_lifetime(db_path, user_ids):
    app = make_app(db_path, LIVE_CHECK_SECONDS=0.1, LIVE_STREAM_SECONDS=0.3)
    client = sign_in(app.test_client(), user_ids["admin"])
    started = time.time()
    body = client.get("/live/stream").get_data(as_text=True)  # buffered: returns when the stream ends
    assert time.time() - started < 5
    assert body.startswith("retry: ")


def test_notifier_wakes_waiters():
    seen = notifier.wait(-1, 0)
    threading.Timer(0.1, notifier.notify).start()
    started = time.time()
    assert notifier.wait(seen, 5) > seen
    assert time.time() - started < 2


def test_live_pages_carry_live_settings(seeded, client):
    body = client.get("/patients/1").get_data(as_text=True)
    assert "data-live" in body and 'data-stream-url="/live/stream"' in body
    assert 'id="live-indicator"' in body and 'id="live-updated"' in body
    for region in ("live-summary", "live-alerts", "live-trend", "live-recent"):
        assert f'id="{region}" data-live-region' in body
    assert 'id="live-results" data-live-region' in client.get("/patients/1/events").get_data(as_text=True)
    assert "data-live" not in client.get("/help").get_data(as_text=True)


# --- database not set up --------------------------------------------------------------

def test_missing_database_shows_friendly_page(tmp_path):
    missing = tmp_path / "nothing-here.sqlite3"
    app = create_app({"DATABASE": str(missing), "SECRET_KEY": "x", "TESTING": False})
    for url in ("/", "/login", "/patients/1", "/help"):
        resp = app.test_client().get(url)
        body = resp.get_data(as_text=True)
        assert resp.status_code == 503
        assert "This dashboard is not ready yet" in body
        assert "Traceback" not in body and "sqlite" not in body.lower()
    assert not missing.exists(), "the app must never create the database itself"
    resp = app.test_client().get("/api/patients")
    assert resp.status_code == 503 and resp.is_json


def test_database_without_schema_shows_friendly_page(tmp_path):
    empty = tmp_path / "empty.sqlite3"
    sqlite3.connect(empty).close()
    app = create_app({"DATABASE": str(empty), "SECRET_KEY": "x"})
    resp = app.test_client().get("/")
    assert resp.status_code == 503 and "not ready yet" in resp.get_data(as_text=True)


def test_missing_secret_key_shows_friendly_page(db_path):
    app = create_app({"DATABASE": str(db_path), "SECRET_KEY": None})
    resp = app.test_client().get("/login")
    assert resp.status_code == 503 and "not ready yet" in resp.get_data(as_text=True)
    assert app.test_client().get("/static/style.css").status_code == 200


def test_unexpected_error_is_friendly(seeded, client, monkeypatch):
    from sage_dashboard import views
    monkeypatch.setattr(views.queries, "count_events", lambda *a, **k: 1 / 0)
    seeded.config["PROPAGATE_EXCEPTIONS"] = False
    resp = client.get("/patients/1")
    body = resp.get_data(as_text=True)
    assert resp.status_code == 500
    assert "Something went wrong on our side" in body and "ZeroDivisionError" not in body


# --- setup commands -------------------------------------------------------------------

def test_init_db_creates_database_and_secrets(tmp_path, capsys):
    db = tmp_path / "new" / "dash.sqlite3"
    assert manage.main(["--db", str(db), "init-db"]) == 0
    assert db.exists()
    secrets_path = config.secrets_file()
    data = json.loads(secrets_path.read_text(encoding="utf-8"))
    assert len(data["secret_key"]) >= 32 and len(data["api_key"]) >= 32
    assert config.load_secret_key() == data["secret_key"] and config.load_api_key() == data["api_key"]
    # running it again changes nothing
    assert manage.main(["--db", str(db), "init-db"]) == 0
    assert json.loads(secrets_path.read_text(encoding="utf-8")) == data
    assert "left unchanged" in capsys.readouterr().out


def test_environment_overrides_secrets_file(tmp_path, monkeypatch):
    manage.main(["--db", str(tmp_path / "d.sqlite3"), "init-db"])
    monkeypatch.setenv("SAGE_SECRET_KEY", "from-env-secret")
    monkeypatch.setenv("SAGE_API_KEY", "from-env-api")
    assert config.load_secret_key() == "from-env-secret" and config.load_api_key() == "from-env-api"


def test_new_api_key_command(tmp_path, capsys):
    manage.main(["--db", str(tmp_path / "d.sqlite3"), "init-db"])
    old = config.load_api_key()
    assert manage.main(["new-api-key"]) == 0
    assert config.load_api_key() != old and config.load_api_key() in capsys.readouterr().out


def test_commands_on_missing_database_say_what_to_do(tmp_path, capsys):
    with pytest.raises(SystemExit):
        manage.main(["--db", str(tmp_path / "none.sqlite3"), "list-users"])
    assert "init-db" in capsys.readouterr().err


def test_load_sample(db_path, capsys):
    assert manage.main(["--db", str(db_path), "load-sample"]) == 0
    conn = queries.connect(db_path)
    assert queries.count_events(conn, 1) == 10
    conn.close()


def test_load_sample_patient_only(db_path):
    assert manage.main(["--db", str(db_path), "load-sample", "--patient-only"]) == 0
    conn = queries.connect(db_path)
    assert len(queries.list_patients(conn)) == 1 and queries.count_events(conn, 1) == 0
    conn.close()


# --- demo replay --------------------------------------------------------------------

def test_demo_shifts_times_to_now_with_fresh_ids():
    data = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    a = demo_replay.shifted_events(data["events"], keep_times=False)
    b = demo_replay.shifted_events(data["events"], keep_times=False)
    assert {e["event_id"] for e in a}.isdisjoint({e["event_id"] for e in b})
    latest = max(e["timestamp"] for e in a)
    assert abs((ago() - __import__("datetime").datetime.fromisoformat(latest)).total_seconds()) < 60
    assert demo_replay.shifted_events(data["events"], keep_times=True) == data["events"]


def test_demo_replay_into_running_dashboard(db_path, user_ids, capsys):
    from werkzeug.serving import make_server
    app = make_app(db_path)
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}"
        assert demo_replay.main(["--url", url, "--delay", "0", "--api-key", API_KEY],
                                sleep=lambda s: None) == 0
        assert demo_replay.main(["--url", url, "--api-key", "wrong"], sleep=lambda s: None) == 1
    finally:
        server.shutdown()
    out = capsys.readouterr()
    assert "[10/10]" in out.out and "added" in out.out
    assert "did not accept the API key" in out.err
    conn = queries.connect(db_path)
    assert queries.count_events(conn, 1) == 10
    conn.close()


def test_demo_replay_when_dashboard_is_not_running(capsys):
    assert demo_replay.main(["--url", "http://127.0.0.1:9", "--api-key", "k"], sleep=lambda s: None) == 1
    assert "Cannot reach the dashboard" in capsys.readouterr().err
