"""Where settings and secrets come from.

Secrets are never written in the code. Each is read from an environment
variable first, then from instance/secrets.json, which `manage.py init-db`
creates with fresh random values on each install (git-ignored).

    SAGE_SECRET_KEY            signs the sign-in cookie
    SAGE_API_KEY               the key the analysis pipeline must send to POST /api/events
    SAGE_DASHBOARD_DB          database file (default instance/sage_dashboard.sqlite3)
    SAGE_INSTANCE_DIR          folder for the database and secrets.json (default dashboard/instance)
    SAGE_TIMEZONE              display time zone, e.g. Asia/Karachi (default: this device's)
    SAGE_SESSION_IDLE_MINUTES  sign out after this long without use (default 60)
"""

import json
import os
import secrets
from pathlib import Path

DEFAULT_INSTANCE_DIR = Path(__file__).resolve().parent.parent / "instance"
SECRETS_FILE_NAME = "secrets.json"


def instance_dir():
    return Path(os.environ.get("SAGE_INSTANCE_DIR") or DEFAULT_INSTANCE_DIR)


def default_database():
    return os.environ.get("SAGE_DASHBOARD_DB") or str(instance_dir() / "sage_dashboard.sqlite3")


def secrets_file():
    return instance_dir() / SECRETS_FILE_NAME


def _read_secrets_file():
    path = secrets_file()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_secret_key():
    return os.environ.get("SAGE_SECRET_KEY") or _read_secrets_file().get("secret_key")


def load_api_key():
    return os.environ.get("SAGE_API_KEY") or _read_secrets_file().get("api_key")


def ensure_secrets_file():
    """Create secrets.json with random keys if it does not exist. Returns (path, created)."""
    path = secrets_file()
    if path.is_file():
        return path, False
    _write_secrets({"secret_key": secrets.token_hex(32), "api_key": secrets.token_urlsafe(32)})
    return path, True


def new_api_key():
    """Replace the API key in secrets.json and return the new key."""
    data = _read_secrets_file()
    data.setdefault("secret_key", secrets.token_hex(32))
    data["api_key"] = secrets.token_urlsafe(32)
    _write_secrets(data)
    return data["api_key"]


def _write_secrets(data):
    path = secrets_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.chmod(path, 0o600)  # owner only; has no effect on Windows
    except OSError:
        pass


def idle_minutes():
    try:
        return max(1, int(os.environ.get("SAGE_SESSION_IDLE_MINUTES", "60")))
    except ValueError:
        return 60
