"""Signing in and out, lockout, inactivity, roles, CSRF and password storage."""

import logging
import re
import time

import pytest

import manage
from conftest import ADMIN, CARER, CSRF, make_app, sign_in
from sage_dashboard import queries

FAILED = "We couldn’t sign you in with those details."


def text(resp):
    return resp.get_data(as_text=True)


def login(client, username, password, token=CSRF, next_url=None):
    data = {"csrf_token": token, "username": username, "password": password}
    if next_url:
        data["next"] = next_url
    return client.post("/login", data=data)


# --- sign in --------------------------------------------------------------------

def test_login_page(anon):
    resp = anon.get("/login")
    assert resp.status_code == 200
    body = text(resp)
    assert "Sign in" in body and 'type="password"' in body and 'autocomplete="current-password"' in body
    assert "Sign out" not in body


def test_correct_login(anon):
    resp = login(anon, ADMIN["username"], ADMIN["password"])
    assert resp.status_code == 302 and resp.headers["Location"] == "/"
    assert "Welcome, Anna." in text(anon.get("/", follow_redirects=True))


def test_login_is_case_insensitive_for_username(anon):
    assert login(anon, "  ANNA ", ADMIN["password"]).status_code == 302


def test_login_follows_safe_next_only(app, anon):
    assert login(anon, "anna", ADMIN["password"], next_url="/help").headers["Location"] == "/help"
    fresh = app.test_client()
    resp = login(fresh, "anna", ADMIN["password"], token=anon_token(fresh), next_url="https://evil.example/")
    assert resp.headers["Location"] == "/"


def anon_token(client):
    return re.search(r'name="csrf_token" value="([^"]+)"', text(client.get("/login"))).group(1)


@pytest.mark.parametrize("username,password", [
    ("anna", "wrong-password"),      # wrong password
    ("nobody", "anna-password-1"),   # unknown user
    ("nobody", "wrong-password"),
])
def test_failed_login_does_not_say_which_part_was_wrong(anon, username, password):
    resp = login(anon, username, password)
    assert resp.status_code == 401
    body = text(resp)
    assert FAILED in body
    assert "unknown" not in body.lower() and "does not exist" not in body.lower()
    assert "incorrect password" not in body.lower()
    with anon.session_transaction() as s:
        assert "user_id" not in s


def test_empty_login(anon):
    resp = login(anon, "", "")
    assert resp.status_code == 400 and "Please enter your username and your password." in text(resp)


def test_lockout_after_repeated_failures(app, anon):
    for _ in range(app.config["LOGIN_MAX_FAILURES"] - 1):
        assert login(anon, "anna", "wrong").status_code == 401
    resp = login(anon, "anna", "wrong")
    assert resp.status_code == 429 and "too many tries" in text(resp)
    # even the right password is refused while paused
    resp = login(anon, "anna", ADMIN["password"])
    assert resp.status_code == 429
    with anon.session_transaction() as s:
        assert "user_id" not in s


def test_lockout_is_the_same_for_unknown_names(app, anon):
    for _ in range(app.config["LOGIN_MAX_FAILURES"]):
        resp = login(anon, "ghost", "wrong")
    assert resp.status_code == 429 and "too many tries" in text(resp)


def test_lockout_ends_and_success_clears_count(app, anon, db_path):
    for _ in range(app.config["LOGIN_MAX_FAILURES"]):
        login(anon, "anna", "wrong")
    conn = queries.connect(db_path)
    queries.save_login_failure(conn, "anna", 5, "2000-01-01T00:00:00Z", "2000-01-01T00:05:00Z")
    conn.close()
    assert login(anon, "anna", ADMIN["password"]).status_code == 302
    conn = queries.connect(db_path)
    assert queries.get_login_failure(conn, "anna") is None
    conn.close()


def test_lockout_window_resets(app, anon, db_path):
    conn = queries.connect(db_path)
    queries.save_login_failure(conn, "anna", 4, "2000-01-01T00:00:00Z", None)  # old window
    conn.close()
    assert login(anon, "anna", "wrong").status_code == 401  # counts as the first failure again
    conn = queries.connect(db_path)
    assert queries.get_login_failure(conn, "anna")["failures"] == 1
    conn.close()


def test_login_requires_csrf(anon):
    assert login(anon, "anna", ADMIN["password"], token="").status_code == 400
    assert login(anon, "anna", ADMIN["password"], token="forged").status_code == 400


def test_session_cookie_is_http_only(anon):
    resp = login(anon, "anna", ADMIN["password"])
    cookie = resp.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie and "SameSite=Strict" in cookie


# --- sign out and expiry ------------------------------------------------------------

def test_logout(client):
    resp = client.post("/logout", data={"csrf_token": CSRF})
    assert resp.status_code == 302 and resp.headers["Location"] == "/login"
    assert "You have signed out." in text(client.get("/login"))
    assert client.get("/patients/1").status_code == 302


def test_logout_needs_csrf_and_post(client):
    assert client.post("/logout").status_code == 400
    assert client.get("/logout").status_code == 405
    assert client.get("/help").status_code == 200  # still signed in


def test_session_expires_after_inactivity(client):
    with client.session_transaction() as s:
        s["last_seen"] = time.time() - 61 * 60
    resp = client.get("/help")
    assert resp.status_code == 302 and resp.headers["Location"].startswith("/login")
    assert "signed out after a while without use" in text(client.get(resp.headers["Location"]))
    with client.session_transaction() as s:
        assert "user_id" not in s


def test_activity_keeps_session_alive(client):
    with client.session_transaction() as s:
        s["last_seen"] = time.time() - 59 * 60
    assert client.get("/help").status_code == 200
    with client.session_transaction() as s:
        assert time.time() - s["last_seen"] < 5


def test_live_requests_do_not_keep_session_alive(seeded, client):
    old = time.time() - 30 * 60
    with client.session_transaction() as s:
        s["last_seen"] = old
    assert client.get("/live/revision").status_code == 200
    assert client.get("/patients/1", headers={"X-Live-Refresh": "1"}).status_code == 200
    with client.session_transaction() as s:
        assert s["last_seen"] == old


def test_expired_session_on_live_request_gets_401(seeded, client):
    with client.session_transaction() as s:
        s["last_seen"] = time.time() - 61 * 60
    resp = client.get("/patients/1", headers={"X-Live-Refresh": "1"})
    assert resp.status_code == 401 and resp.get_json()["reason"] == "expired"


def test_removed_user_is_signed_out(client, db_path, user_ids):
    conn = queries.connect(db_path)
    queries.delete_user(conn, user_ids["admin"])
    conn.close()
    assert client.get("/help").status_code == 302


# --- protected pages ----------------------------------------------------------------

@pytest.mark.parametrize("url", ["/", "/patients/1", "/patients/1/events", "/help", "/import", "/users"])
def test_pages_need_sign_in(anon, url):
    resp = anon.get(url)
    assert resp.status_code == 302
    assert resp.headers["Location"].startswith("/login?next=")


@pytest.mark.parametrize("url", ["/api/health", "/api/patients", "/api/patients/1",
                                 "/api/patients/1/events", "/api/patients/1/gait-trend",
                                 "/live/revision", "/live/stream"])
def test_api_and_live_need_sign_in(anon, url):
    resp = anon.get(url)
    assert resp.status_code == 401 and resp.is_json


@pytest.mark.parametrize("url", ["/events/1/check", "/events/1/uncheck", "/import", "/users", "/users/1/remove"])
def test_actions_need_sign_in(anon, url):
    resp = anon.post(url, data={"csrf_token": CSRF})
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]


def test_login_redirects_back_after_sign_in(anon):
    resp = anon.get("/help")
    target = resp.headers["Location"]
    page = text(anon.get(target))
    assert 'name="next" value="/help"' in page
    assert login(anon, "anna", ADMIN["password"], next_url="/help").headers["Location"] == "/help"


# --- roles ------------------------------------------------------------------------

@pytest.mark.parametrize("method,url", [("get", "/import"), ("post", "/import"),
                                        ("get", "/users"), ("post", "/users"),
                                        ("post", "/users/1/remove")])
def test_caregiver_cannot_manage(carer, method, url):
    resp = getattr(carer, method)(url, data={"csrf_token": CSRF}) if method == "post" else carer.get(url)
    assert resp.status_code == 403
    assert "Only the person who manages this dashboard can do this." in text(resp)


def test_caregiver_navigation_hides_manager_pages(carer):
    body = text(carer.get("/help"))
    assert "Add results" not in body and "Who can sign in" not in body
    assert "Signed in as <strong>Carl</strong>" in body


def test_admin_navigation_shows_manager_pages(client):
    body = text(client.get("/help"))
    assert "Add results" in body and "Who can sign in" in body


# --- CSRF on every form ---------------------------------------------------------------

@pytest.mark.parametrize("url", ["/events/1/check", "/events/1/uncheck", "/import", "/users",
                                 "/users/2/remove", "/logout"])
def test_state_changing_requests_need_csrf(seeded, client, url):
    assert client.post(url, data={}).status_code == 400
    assert client.post(url, data={"csrf_token": "forged"}).status_code == 400


def test_csrf_header_is_accepted(seeded, client):
    resp = client.post("/events/1/check", headers={"X-CSRF-Token": CSRF})
    assert resp.status_code == 302


# --- passwords --------------------------------------------------------------------

def test_passwords_are_hashed_never_plain(db_path, user_ids):
    raw = db_path.read_bytes()
    for user in (ADMIN, CARER):
        assert user["password"].encode() not in raw
    conn = queries.connect(db_path)
    for u in queries.list_users(conn):
        assert u["password_hash"].startswith(("scrypt:", "pbkdf2:"))
    conn.close()


def test_passwords_never_logged(anon, caplog, capsys):
    caplog.set_level(logging.DEBUG)
    login(anon, "anna", ADMIN["password"])
    login(anon, "anna", "a-wrong-secret-xyz")
    captured = capsys.readouterr()
    everything = caplog.text + captured.out + captured.err
    assert ADMIN["password"] not in everything and "a-wrong-secret-xyz" not in everything


def test_no_hard_coded_credentials_in_code():
    from conftest import DASHBOARD_DIR
    for path in list((DASHBOARD_DIR / "sage_dashboard").glob("*.py")) + [DASHBOARD_DIR / "manage.py"]:
        code = path.read_text(encoding="utf-8")
        assert not re.search(r"(password|secret_key|api_key)\s*=\s*[\"'][^\"']{4,}[\"']", code, re.I), path.name


# --- managing users ---------------------------------------------------------------

def new_user(client, **changes):
    data = {"csrf_token": CSRF, "display_name": "Sara", "username": "sara", "role": "caregiver",
            "password": "sara-password", "password_again": "sara-password", **changes}
    return client.post("/users", data=data)


def test_admin_adds_user_who_can_then_sign_in(app, client, db_path):
    resp = new_user(client)
    assert resp.status_code == 302
    assert "Sara can now sign in" in text(client.get("/users"))
    conn = queries.connect(db_path)
    user = queries.get_user_by_username(conn, "sara")
    conn.close()
    assert user["role"] == "caregiver" and "sara-password" not in user["password_hash"]
    fresh = app.test_client()
    assert login(fresh, "sara", "sara-password", token=anon_token(fresh)).status_code == 302


@pytest.mark.parametrize("changes,message", [
    ({"username": "x"}, "The username should be 3 to 32"),
    ({"username": "has space"}, "The username should be 3 to 32"),
    ({"display_name": ""}, "Please give a name"),
    ({"password": "short", "password_again": "short"}, "at least 8 characters"),
    ({"password_again": "different-one"}, "The two passwords are not the same"),
    ({"role": "owner"}, "Please choose what this person is allowed to do"),
    ({"username": "carl"}, "Someone already has that username"),
])
def test_add_user_problems(client, changes, message):
    resp = new_user(client, **changes)
    assert resp.status_code == 400 and message in text(resp)


def test_remove_user(client, user_ids):
    resp = client.post(f"/users/{user_ids['caregiver']}/remove", data={"csrf_token": CSRF})
    assert resp.status_code == 302
    assert "Carl can no longer sign in." in text(client.get("/users"))


def test_cannot_remove_self(client, user_ids):
    client.post(f"/users/{user_ids['admin']}/remove", data={"csrf_token": CSRF})
    assert "You cannot remove yourself." in text(client.get("/users"))


def test_manager_can_remove_another_manager(client, db_path):
    conn = queries.connect(db_path)
    other = queries.create_user(conn, "boss", "Boss", "scrypt:" + "x" * 40, "admin")
    conn.close()
    resp = client.post(f"/users/{other}/remove", data={"csrf_token": CSRF})
    assert "Boss can no longer sign in." in text(client.get(resp.headers["Location"]))
    conn = queries.connect(db_path)
    assert queries.count_admins(conn) == 1
    conn.close()


def test_remove_unknown_user(client):
    assert client.post("/users/999/remove", data={"csrf_token": CSRF}).status_code == 404


# --- command line users -------------------------------------------------------------

def test_create_user_command_hashes_and_does_not_echo(db_path, monkeypatch, capsys):
    answers = iter(["new-password-1", "new-password-1"])
    monkeypatch.setattr(manage.getpass, "getpass", lambda prompt="": next(answers))
    code = manage.main(["--db", str(db_path), "create-user", "--username", "Dina",
                        "--name", "Dina", "--role", "admin"])
    assert code == 0
    out = capsys.readouterr()
    assert "new-password-1" not in out.out + out.err
    conn = queries.connect(db_path)
    user = queries.get_user_by_username(conn, "dina")
    conn.close()
    assert user["role"] == "admin" and user["password_hash"].startswith(("scrypt:", "pbkdf2:"))


def test_create_user_command_rejects_mismatch_and_short(db_path, monkeypatch, capsys):
    answers = iter(["aaaaaaaa1", "bbbbbbbb2"] * 3)
    monkeypatch.setattr(manage.getpass, "getpass", lambda prompt="": next(answers))
    with pytest.raises(SystemExit):
        manage.main(["--db", str(db_path), "create-user", "--username", "eve", "--name", "Eve",
                     "--role", "caregiver"])
    answers2 = iter(["short", "short"])
    monkeypatch.setattr(manage.getpass, "getpass", lambda prompt="": next(answers2))
    assert manage.main(["--db", str(db_path), "create-user", "--username", "eve", "--name", "Eve",
                        "--role", "caregiver"]) == 1
    assert "at least 8 characters" in capsys.readouterr().err


def test_create_user_command_duplicate(db_path, user_ids, capsys):
    assert manage.main(["--db", str(db_path), "create-user", "--username", "anna", "--name", "A",
                        "--role", "admin"]) == 1
    assert "already has the username" in capsys.readouterr().err


def test_set_password_and_list_users_commands(db_path, user_ids, monkeypatch, capsys, app):
    answers = iter(["fresh-password-9", "fresh-password-9"])
    monkeypatch.setattr(manage.getpass, "getpass", lambda prompt="": next(answers))
    assert manage.main(["--db", str(db_path), "set-password", "carl"]) == 0
    assert manage.main(["--db", str(db_path), "list-users"]) == 0
    out = capsys.readouterr().out
    assert "carl" in out and "anna" in out and "fresh-password-9" not in out
    fresh = app.test_client()
    assert login(fresh, "carl", "fresh-password-9", token=anon_token(fresh)).status_code == 302
    assert manage.main(["--db", str(db_path), "set-password", "nobody"]) == 1


def test_no_users_yet_message(db_path):
    app = make_app(db_path)
    page = app.test_client().get("/login").get_data(as_text=True)
    assert "Nobody has been given a sign-in yet." in page
