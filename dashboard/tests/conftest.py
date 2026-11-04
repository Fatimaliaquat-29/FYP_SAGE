import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

DASHBOARD_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DASHBOARD_DIR))

from sage_dashboard import create_app, queries  # noqa: E402
from sage_dashboard.auth import hash_password  # noqa: E402
from sage_dashboard.sources import JsonFileSource, ingest  # noqa: E402

SAMPLE_FILE = DASHBOARD_DIR / "sample_data" / "sample_events.json"
CSRF = "test-csrf-token"
API_KEY = "test-api-key-0123456789"
ADMIN = {"username": "anna", "name": "Anna", "password": "anna-password-1"}
CARER = {"username": "carl", "name": "Carl", "password": "carl-password-1"}


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat()


def ago(**kwargs):
    return datetime.now(timezone.utc) - timedelta(**kwargs)


def patient(pid="P001", name="Amina Rahman", age=81, room="Bedroom", **extra):
    return {"id": pid, "name": name, "age": age, "room": room, **extra}


def fall(n, when, pid="P001", **extra):
    return {"event_id": f"fall-{n}", "patient": pid, "timestamp": iso(when),
            "type": "fall", "confidence": 0.9, **extra}


def gait(n, when, risk, pid="P001", **extra):
    return {"event_id": f"gait-{n}", "patient": pid, "timestamp": iso(when),
            "type": "gait_risk", "confidence": 0.8, "risk_score": risk, **extra}


def payload(events, patients=None):
    return json.dumps({"format_version": 1,
                       "patients": [patient()] if patients is None else patients,
                       "events": events}).encode("utf-8")


def load(conn, raw, filename="test.json"):
    return ingest(conn, JsonFileSource(raw, filename=filename))


def seed_events():
    return [
        fall(1, ago(hours=2)),
        fall(2, ago(days=10), severity="medium"),
        gait(1, ago(days=20), 0.25),
        gait(2, ago(days=12), 0.45),
        gait(3, ago(days=3), 0.75),
        gait(4, ago(days=1), 0.30),
    ]


def add_users(db_path):
    conn = queries.connect(db_path)
    ids = {}
    for user, role in ((ADMIN, "admin"), (CARER, "caregiver")):
        ids[role] = queries.create_user(conn, user["username"], user["name"],
                                        hash_password(user["password"]), role)
    conn.close()
    return ids


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path, monkeypatch):
    """No test may read or write the real instance folder or real keys."""
    monkeypatch.setenv("SAGE_INSTANCE_DIR", str(tmp_path / "instance"))
    for name in ("SAGE_SECRET_KEY", "SAGE_API_KEY", "SAGE_DASHBOARD_DB", "SAGE_TIMEZONE",
                 "SAGE_SESSION_IDLE_MINUTES"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.sqlite3"
    queries.create_database(path)
    return path


@pytest.fixture
def conn(db_path):
    c = queries.connect(db_path)
    yield c
    c.close()


@pytest.fixture
def user_ids(db_path):
    return add_users(db_path)


def make_app(db_path, **overrides):
    return create_app({"DATABASE": str(db_path), "SECRET_KEY": "test-secret", "API_KEY": API_KEY,
                       "TIMEZONE": "UTC", "TESTING": True, **overrides})


@pytest.fixture
def app(db_path, user_ids):
    return make_app(db_path)


def sign_in(client, user_id):
    with client.session_transaction() as s:
        s["user_id"] = user_id
        s["last_seen"] = time.time()
        s["csrf_token"] = CSRF
    return client


@pytest.fixture
def anon(app):
    """Not signed in, but holding a CSRF token like a browser that loaded a form."""
    c = app.test_client()
    with c.session_transaction() as s:
        s["csrf_token"] = CSRF
    return c


@pytest.fixture
def client(app, user_ids):
    """Signed in as an admin."""
    return sign_in(app.test_client(), user_ids["admin"])


@pytest.fixture
def carer(app, user_ids):
    """Signed in as a caregiver."""
    return sign_in(app.test_client(), user_ids["caregiver"])


@pytest.fixture
def seeded(app, db_path):
    """One person with a known mix of events, all recent."""
    c = queries.connect(db_path)
    result = load(c, payload(seed_events()))
    c.close()
    assert result.added == 6
    return app
