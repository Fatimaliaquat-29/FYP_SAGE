"""Every page and read-only API endpoint, signed in, including error responses."""

import io
import re
from datetime import timedelta

import pytest

from conftest import CSRF, SAMPLE_FILE, ago, fall, load, patient, payload
from sage_dashboard import queries
from sage_dashboard.presenters import now_utc


def text(resp):
    return resp.get_data(as_text=True)


def visible(resp):
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text(resp), flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))


def add(app, events, patients=None):
    conn = queries.connect(app.config["DATABASE"])
    result = load(conn, payload(events, patients))
    conn.close()
    return result


def open_event_ids(app, patient_id=1):
    conn = queries.connect(app.config["DATABASE"])
    ids = [r["id"] for r in queries.query_events(conn, patient_id, open_only=True)]
    conn.close()
    return ids


# --- home ---------------------------------------------------------------------------

def test_home_empty_shows_welcome(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Welcome to S.A.G.E." in text(resp)
    assert 'href="/import"' in text(resp)


def test_home_empty_for_caregiver_has_no_add_button(carer):
    body = text(carer.get("/"))
    assert "will add them for you" in body and 'href="/import"' not in body


def test_home_single_patient_redirects(seeded, client):
    resp = client.get("/")
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/patients/1")


def test_home_lists_several_people_with_summary(app, client):
    add(app, [fall(1, ago(hours=1), pid="P2")], patients=[patient("P1", "Ann Lee"), patient("P2", "Bob Khan")])
    body = text(client.get("/"))
    assert "The people you look after" in body and "Ann Lee" in body and "Bob Khan" in body
    assert "Bob may need you now." in body
    assert "No news yet" in body


# --- overview -----------------------------------------------------------------------

def test_overview_answers_at_a_glance(seeded, client):
    body = text(client.get("/patients/1"))
    assert "Amina Rahman" in body and "Bedroom" in body
    assert "Needs your attention" in body
    assert "Amina may need you now." in body
    assert "Check on Amina straight away" in body
    assert "I’ve checked on Amina" in body
    assert body.count("Not available yet") == 2
    assert body.count('class="trend-dot"') == 4
    assert "Amina was seen walking 4 times" in body
    assert "What the labels mean" in body


def test_overview_uses_preferred_name(app, client):
    add(app, [fall(1, ago(hours=1))], patients=[patient(preferred_name="Nani")])
    body = text(client.get("/patients/1"))
    assert "Nani may need you now." in body and "I’ve checked on Nani" in body


def test_overview_all_is_well_after_checking(seeded, client):
    for event_id in open_event_ids(seeded):
        client.post(f"/events/{event_id}/check", data={"csrf_token": CSRF})
    body = text(client.get("/patients/1"))
    assert "All is well" in body and "All is well with Amina." in body
    assert "There is nothing you need to do right now." in body
    assert "Please check on" not in body


def test_overview_medium_only_is_not_urgent(app, client):
    add(app, [fall(1, ago(hours=1), severity="medium")])
    body = text(client.get("/patients/1"))
    assert "Nothing urgent, but something is worth a look." in body


def test_overview_trend_ranges(seeded, client):
    assert text(client.get("/patients/1?range=7")).count('class="trend-dot"') == 2
    assert text(client.get("/patients/1?range=all")).count('class="trend-dot"') == 4


def test_overview_empty_patient(app, client):
    add(app, [], patients=[patient("P1", "Ann Lee"), patient("P2", "Bob Khan")])
    body = text(client.get("/patients/1"))
    assert "No news about Ann yet." in body
    assert "Ann has not been seen walking in this time." in body
    assert "Nothing has been seen yet." in body
    assert body.count("Not available yet") == 2


def test_overview_unknown_patient(client):
    resp = client.get("/patients/42")
    assert resp.status_code == 404
    assert "We could not find that person." in text(resp)


def test_overview_bad_range(seeded, client):
    resp = client.get("/patients/1?range=forever")
    assert resp.status_code == 400
    assert "That time period is not one we know." in text(resp)


TECH = re.compile(r"\b(model|confidence|gait|pipeline|json|api|score|probability|anomaly|algorithm|null|none)\b", re.I)
CODES = re.compile(r"\b(400|401|403|404|405|413|415|422|429|500|503)\b")


@pytest.mark.parametrize("url", ["/patients/1", "/patients/1?range=all", "/patients/1/events",
                                 "/patients/1/events?type=trip", "/import", "/users", "/help",
                                 "/patients/99", "/nothing-here"])
def test_no_technical_words_or_error_codes_on_screen(seeded, client, url):
    words = visible(client.get(url))
    assert not TECH.search(words), TECH.search(words)
    assert not CODES.search(words), CODES.search(words)
    assert "Traceback" not in words


def test_no_technical_words_after_import(client):
    raw = payload([fall(1, ago(hours=1)), {"patient": "P001", "type": "fall"}])
    words = visible(upload(client, raw))
    assert not TECH.search(words), TECH.search(words)
    words = visible(upload(client, b"{broken"))
    assert not TECH.search(words), TECH.search(words)


# --- events -------------------------------------------------------------------------

def rows(resp):
    return re.findall(r'class="event-row" data-type="(\w+)" data-severity="(\w+)"', text(resp))


def test_events_all(seeded, client):
    resp = client.get("/patients/1/events")
    assert resp.status_code == 200
    assert len(rows(resp)) == 6 and "6 things so far" in text(resp)


def test_events_filter_type_and_severity(seeded, client):
    assert {t for t, _ in rows(client.get("/patients/1/events?type=fall"))} == {"fall"}
    assert len(rows(client.get("/patients/1/events?type=fall"))) == 2
    resp = client.get("/patients/1/events?type=gait_risk&severity=high")
    assert rows(resp) == [("gait_risk", "high")]
    assert "1 thing matches your choices" in text(resp)


def test_events_filter_dates(seeded, client):
    today = now_utc().date()
    start, end = (today - timedelta(days=4)).isoformat(), (today - timedelta(days=2)).isoformat()
    assert rows(client.get(f"/patients/1/events?from={start}&to={end}")) == [("gait_risk", "high")]
    yesterday = (today - timedelta(days=1)).isoformat()
    got = rows(client.get(f"/patients/1/events?from={yesterday}&to={today.isoformat()}"))
    assert ("fall", "high") in got and ("gait_risk", "low") in got


def test_events_no_match_empty_state(seeded, client):
    body = text(client.get("/patients/1/events?from=2001-01-01&to=2001-01-02"))
    assert "Nothing matches these choices" in body and "Show everything" in body


def test_events_none_recorded(app, client):
    add(app, [])
    assert "Nothing has been seen for Amina yet." in text(client.get("/patients/1/events"))


@pytest.mark.parametrize("query,fragment", [
    ("type=trip", "could not be understood"),
    ("severity=critical", "could not be understood"),
    ("from=yesterday", "dates could not be understood"),
    ("to=2026-13-01", "dates could not be understood"),
    ("from=2026-11-05&to=2026-11-01", "is after the"),
    ("page=0", "could not be understood"),
    ("page=abc", "could not be understood"),
])
def test_events_bad_filters(seeded, client, query, fragment):
    resp = client.get(f"/patients/1/events?{query}")
    assert resp.status_code == 400
    assert fragment in text(resp) and 'role="alert"' in text(resp)


def test_events_pagination(app, client):
    add(app, [fall(i, ago(hours=i + 1)) for i in range(30)])
    first = client.get("/patients/1/events")
    assert len(rows(first)) == 25 and "Page 1 of 2" in text(first)
    assert len(rows(client.get("/patients/1/events?page=2"))) == 5
    assert len(rows(client.get("/patients/1/events?page=99"))) == 5


def test_events_unknown_patient(client):
    assert client.get("/patients/9/events").status_code == 404


# --- "I've checked" and undo --------------------------------------------------------

def test_check_and_undo(seeded, client):
    event_id = open_event_ids(seeded)[0]
    resp = client.post(f"/events/{event_id}/check",
                       data={"csrf_token": CSRF, "next": "/patients/1/events?type=fall"})
    assert resp.status_code == 302 and resp.headers["Location"] == "/patients/1/events?type=fall"
    assert event_id not in open_event_ids(seeded)
    follow = text(client.get(resp.headers["Location"]))
    assert "This is now marked as checked on Amina." in follow
    assert f'action="/events/{event_id}/uncheck"' in follow and ">Undo<" in follow
    assert "Checked by Anna, today at" in follow

    resp = client.post(f"/events/{event_id}/uncheck", data={"csrf_token": CSRF})
    assert resp.status_code == 302
    assert event_id in open_event_ids(seeded)
    assert "back on the list of things to check" in text(client.get(resp.headers["Location"]))


def test_caregiver_can_check(seeded, carer):
    event_id = open_event_ids(seeded)[0]
    assert carer.post(f"/events/{event_id}/check", data={"csrf_token": CSRF}).status_code == 302
    assert event_id not in open_event_ids(seeded)


@pytest.mark.parametrize("target", ["https://example.com/", "//example.com/x", "javascript:alert(1)"])
def test_check_ignores_outside_redirects(seeded, client, target):
    event_id = open_event_ids(seeded)[0]
    resp = client.post(f"/events/{event_id}/check", data={"csrf_token": CSRF, "next": target})
    assert resp.headers["Location"] == "/patients/1"


def test_check_unknown_event(client):
    assert client.post("/events/999/check", data={"csrf_token": CSRF}).status_code == 404
    assert client.post("/events/999/uncheck", data={"csrf_token": CSRF}).status_code == 404


def test_check_get_not_allowed(seeded, client):
    resp = client.get("/events/1/check")
    assert resp.status_code == 405
    assert "That did not work from here" in text(resp)


# --- adding results (import) still works ---------------------------------------------

def upload(client, raw, name="results.json", token=CSRF):
    data = {"file": (io.BytesIO(raw), name)}
    if token is not None:
        data["csrf_token"] = token
    return client.post("/import", data=data, content_type="multipart/form-data")


def test_import_page(client):
    resp = client.get("/import")
    assert resp.status_code == 200
    assert 'type="file"' in text(resp) and "Add these results" in text(resp)


def test_import_upload_valid_then_duplicate(client):
    body = text(upload(client, SAMPLE_FILE.read_bytes(), "sample_events.json"))
    assert "Done, the results have been added" in body and "<strong>10</strong> new things added" in body
    body = text(upload(client, SAMPLE_FILE.read_bytes(), "sample_events.json"))
    assert "<strong>0</strong> new things added" in body and "<strong>10</strong> already here" in body
    assert "Added recently" in body and "sample_events" in body and "by Anna" in body
    assert "sample_events.json" not in body


def test_import_upload_partial(client):
    raw = payload([fall(1, ago(hours=1)), {"patient": "P001", "type": "fall"}])
    body = text(upload(client, raw))
    assert "<strong>1</strong> new thing added" in body
    assert "Entry 2:" in body and "The date and time is missing." in body


@pytest.mark.parametrize("raw,fragment", [
    (b"", "The file is empty."),
    (b"{broken", "This file can&#39;t be read"),
    (b"{\"events\": []}", "There was nothing in the file to add."),
])
def test_import_upload_bad_files(client, raw, fragment):
    resp = upload(client, raw)
    assert resp.status_code == 400
    assert "Nothing was added" in text(resp) and fragment in text(resp)


def test_import_without_file(client):
    resp = client.post("/import", data={"csrf_token": CSRF}, content_type="multipart/form-data")
    assert resp.status_code == 400 and "Please choose a file first" in text(resp)


def test_import_without_csrf(client):
    assert upload(client, SAMPLE_FILE.read_bytes(), token=None).status_code == 400


def test_import_too_large(app, client):
    app.config["MAX_CONTENT_LENGTH"] = 1024
    resp = upload(client, b" " * 4096)
    assert resp.status_code == 413 and "That file is too large" in text(resp)


# --- help, errors and assets ---------------------------------------------------------

def test_help_page(client):
    body = text(client.get("/help"))
    assert "How to use this page" in body
    assert "I see an Urgent alert?" in body and "I press “I’ve checked on…”?" in body
    for label in ("Urgent", "Worth a look", "For information"):
        assert label in body


def test_unknown_page(client):
    resp = client.get("/no/such/page")
    assert resp.status_code == 404 and "We could not find that page" in text(resp)


def test_static_files(client):
    assert client.get("/static/style.css").mimetype == "text/css"
    assert client.get("/static/app.js").status_code == 200


@pytest.mark.parametrize("url", ["/", "/patients/1", "/patients/1/events", "/import", "/help",
                                 "/users", "/static/style.css", "/static/app.js"])
def test_nothing_loaded_from_the_internet(seeded, client, url):
    body = text(client.get(url, follow_redirects=True))
    assert not re.search(r"(src|href|action)=\"(https?:)?//", body)
    assert "@import" not in body and "url(http" not in body
    assert not re.search(r"fetch\(\s*[\"']https?:", body)


# --- read-only API --------------------------------------------------------------------

def test_api_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}


def test_api_patients(client, seeded):
    p = client.get("/api/patients").get_json()["patients"][0]
    assert p["name"] == "Amina Rahman" and p["status"]["state"] == "attention"


def test_api_patients_empty(client):
    assert client.get("/api/patients").get_json() == {"patients": []}


def test_api_patient(seeded, client):
    data = client.get("/api/patients/1").get_json()
    assert data["patient"]["external_id"] == "P001" and data["patient"]["status"]["open_alerts"] == 4


def test_api_patient_404(client):
    resp = client.get("/api/patients/5")
    assert resp.status_code == 404 and resp.get_json()["error"] == "Not Found"


def test_api_events(seeded, client):
    data = client.get("/api/patients/1/events").get_json()
    assert data["total"] == 6 and len(data["events"]) == 6
    assert data["events"][0]["headline"].startswith("Possible fall at")
    assert data["events"] == sorted(data["events"], key=lambda e: e["occurred_at"], reverse=True)
    data = client.get("/api/patients/1/events?type=gait_risk&severity=low,medium&limit=1&offset=1").get_json()
    assert (data["total"], len(data["events"])) == (3, 1)


@pytest.mark.parametrize("query", ["type=trip", "from=bad", "limit=0", "limit=abc",
                                   "limit=501", "offset=-1", "from=2026-02-02&to=2026-01-01"])
def test_api_events_bad_query(seeded, client, query):
    resp = client.get(f"/api/patients/1/events?{query}")
    assert resp.status_code == 400 and resp.get_json()["message"]


def test_api_events_unknown_patient(client):
    assert client.get("/api/patients/3/events").status_code == 404


def test_api_gait_trend(seeded, client):
    data = client.get("/api/patients/1/gait-trend?range=all").get_json()
    assert [p["risk_score"] for p in data["points"]] == [0.25, 0.45, 0.75, 0.30]
    assert len(client.get("/api/patients/1/gait-trend?range=7").get_json()["points"]) == 2
    assert client.get("/api/patients/1/gait-trend").get_json()["range"] == "30"


def test_api_gait_trend_errors(seeded, client):
    assert client.get("/api/patients/1/gait-trend?range=1y").status_code == 400
    assert client.get("/api/patients/8/gait-trend").status_code == 404


def test_api_unknown_endpoint_and_method(client):
    resp = client.get("/api/nothing")
    assert resp.status_code == 404 and resp.is_json
    resp = client.post("/api/patients", headers={"X-CSRF-Token": CSRF})
    assert resp.status_code == 405 and resp.is_json
