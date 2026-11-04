"""Set up and run the S.A.G.E. dashboard.

    python dashboard/manage.py init-db               create the database from schema.sql (safe to repeat)
    python dashboard/manage.py create-user           add someone who can sign in (asks for a password)
    python dashboard/manage.py set-password NAME     give someone a new password
    python dashboard/manage.py list-users            show who can sign in
    python dashboard/manage.py load-sample           add the sample person and their history
    python dashboard/manage.py load-sample --patient-only   add only the sample person
    python dashboard/manage.py import FILE           add a results file
    python dashboard/manage.py new-api-key           make a new key for the pipeline
    python dashboard/manage.py run [--host H] [--port P]    start the dashboard
    python dashboard/manage.py demo [--video FILE]   start the dashboard AND live video processing

Add --db PATH before the command to use a different database file.
"""

import argparse
import getpass
import json
import sys
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DASHBOARD_DIR))

from sage_dashboard import config, create_app, queries  # noqa: E402
from sage_dashboard.auth import hash_password, normalise_username, validate_new_user  # noqa: E402
from sage_dashboard.sources import JsonFileSource, ingest  # noqa: E402

SAMPLE_FILE = DASHBOARD_DIR / "sample_data" / "sample_events.json"
DEFAULT_DEMO_VIDEO = DASHBOARD_DIR.parent / "test_footage" / "Hussain Testing 7-30-26" / "Moving_in_out_frame_withFall.MOV"


def _connect(args):
    try:
        return queries.connect(args.db)
    except queries.DatabaseNotReady:
        print(f"The database at {args.db} is not set up yet. Run: python dashboard/manage.py init-db",
              file=sys.stderr)
        raise SystemExit(2)


def cmd_init_db(args):
    queries.create_database(args.db)
    print(f"Database ready: {args.db}")
    path, created = config.ensure_secrets_file()
    if created:
        print(f"Created {path} with a new secret key and API key (keep this file private).")
    else:
        print(f"Keys already exist in {path}; left unchanged.")
    print("Next: python dashboard/manage.py create-user")
    return 0


def _ask(prompt, given=None):
    if given:
        return given
    return input(prompt).strip()


def _ask_password():
    for _ in range(3):
        first = getpass.getpass("Password (not shown as you type): ")
        second = getpass.getpass("Type it again: ")
        if first != second:
            print("The two passwords were not the same. Please try again.")
            continue
        return first
    raise SystemExit("Giving up after three tries.")


def cmd_create_user(args):
    conn = _connect(args)
    try:
        username = normalise_username(_ask("Username (what they type to sign in): ", args.username))
        display = _ask("Name to show on screen: ", args.name)
        role = args.role or ("admin" if queries.count_admins(conn) == 0 else "caregiver")
        if not args.role:
            answer = _ask(f"Role, 'caregiver' or 'admin' [{role}]: ")
            role = answer or role
        if queries.get_user_by_username(conn, username):
            print(f"Someone already has the username '{username}'.", file=sys.stderr)
            return 1
        password = _ask_password()
        problems = validate_new_user(username, display, password, role)
        if problems:
            for problem in problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
        queries.create_user(conn, username, display, hash_password(password), role)
        print(f"Done. {display} can now sign in as '{username}' ({role}).")
        return 0
    finally:
        conn.close()


def cmd_set_password(args):
    conn = _connect(args)
    try:
        user = queries.get_user_by_username(conn, normalise_username(args.username))
        if user is None:
            print(f"No one has the username '{args.username}'.", file=sys.stderr)
            return 1
        password = _ask_password()
        problems = validate_new_user(user["username"], user["display_name"], password, user["role"])
        if problems:
            for problem in problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
        queries.set_password_hash(conn, user["id"], hash_password(password))
        queries.clear_login_failures(conn, user["username"])
        print(f"Done. {user['display_name']} has a new password.")
        return 0
    finally:
        conn.close()


def cmd_list_users(args):
    conn = _connect(args)
    try:
        users = queries.list_users(conn)
        if not users:
            print("No one can sign in yet. Run: python dashboard/manage.py create-user")
        for u in users:
            print(f"{u['username']:<20} {u['role']:<10} {u['display_name']}")
        return 0
    finally:
        conn.close()


def _import_bytes(args, raw, filename):
    conn = _connect(args)
    try:
        result = ingest(conn, JsonFileSource(raw, filename=filename))
    finally:
        conn.close()
    if result.error:
        print(result.error, file=sys.stderr)
    print(f"{result.added} added, {result.duplicates} already present, {result.rejected} rejected")
    for problem in result.problems:
        print(f"  {problem.where}: {problem.technical}")
    return 1 if result.error and not (result.added or result.patients_added or result.patients_updated) else 0


def cmd_import(args):
    if not args.file.is_file():
        print(f"No such file: {args.file}", file=sys.stderr)
        return 2
    return _import_bytes(args, args.file.read_bytes(), args.file.name)


def cmd_load_sample(args):
    data = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    if args.patient_only:
        data = {"format_version": data["format_version"], "patients": data["patients"], "events": []}
    return _import_bytes(args, json.dumps(data).encode("utf-8"), SAMPLE_FILE.name)


def cmd_new_api_key(args):
    key = config.new_api_key()
    print(f"New API key saved in {config.secrets_file()}:")
    print(key)
    print("Give this key to the pipeline (header 'Authorization: Bearer <key>'). Restart the dashboard to use it.")
    if config.os.environ.get("SAGE_API_KEY"):
        print("Note: SAGE_API_KEY is set in your environment and takes priority over this file.")
    return 0


def cmd_run(args):
    app = create_app({"DATABASE": args.db})
    if not app.config.get("SECRET_KEY"):
        print("No secret key yet. Run: python dashboard/manage.py init-db", file=sys.stderr)
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
    return 0


def cmd_demo(args):
    """One command for the live demo: set up if needed, start processing, serve the pages."""
    from sage_dashboard import demo_service
    video = Path(args.video) if args.video else DEFAULT_DEMO_VIDEO
    if not video.is_file():
        print(f"Video not found: {video}. Choose one with --video PATH", file=sys.stderr)
        return 2
    queries.create_database(args.db)          # safe to repeat; adds the demo log table if missing
    config.ensure_secrets_file()
    conn = queries.connect(args.db)
    try:
        if queries.get_patient_id_by_external(conn, args.patient) is None:
            if args.patient != "P001":
                print(f"No person with id '{args.patient}'. Add them first (import or load-sample).",
                      file=sys.stderr)
                return 2
            data = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
            ingest(conn, JsonFileSource(json.dumps({"format_version": 1, "patients": data["patients"],
                                                    "events": []}).encode("utf-8"), SAMPLE_FILE.name))
        no_users = queries.count_users(conn) == 0
    finally:
        conn.close()
    if no_users:
        print("Nobody can sign in yet. In another window run: python dashboard/manage.py create-user")

    from sage_dashboard.demo_service import SagePipeline
    pipeline = SagePipeline(use_lstm=not args.no_lstm, use_objects=not args.no_objects,
                            object_model=args.object_model, use_gait=not args.no_gait)
    demo_service.start_service(video_path=video, db_path=args.db, pipeline=pipeline,
                               patient_external_id=args.patient)
    print(f"Processing {video.name} in the background (models are loading; this can take a minute).")
    print(f"Open http://{'127.0.0.1' if args.host == '0.0.0.0' else args.host}:{args.port}/demo")
    app = create_app({"DATABASE": args.db})
    try:
        # No reloader: it would start a second process with a second copy of the models.
        app.run(host=args.host, port=args.port, debug=False, threaded=True, use_reloader=False)
    finally:
        demo_service.stop_service()
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="S.A.G.E. care dashboard")
    parser.add_argument("--db", default=None, help="database file (default: dashboard/instance/sage_dashboard.sqlite3)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db", help="create the database from schema.sql").set_defaults(func=cmd_init_db)
    p = sub.add_parser("create-user", help="add someone who can sign in")
    p.add_argument("--username")
    p.add_argument("--name")
    p.add_argument("--role", choices=queries.ROLES)
    p.set_defaults(func=cmd_create_user)
    p = sub.add_parser("set-password", help="give someone a new password")
    p.add_argument("username")
    p.set_defaults(func=cmd_set_password)
    sub.add_parser("list-users", help="show who can sign in").set_defaults(func=cmd_list_users)
    p = sub.add_parser("load-sample", help="add the sample person")
    p.add_argument("--patient-only", action="store_true", help="add the person but none of their history")
    p.set_defaults(func=cmd_load_sample)
    p = sub.add_parser("import", help="add a results file")
    p.add_argument("file", type=Path)
    p.set_defaults(func=cmd_import)
    sub.add_parser("new-api-key", help="make a new key for the pipeline").set_defaults(func=cmd_new_api_key)
    p = sub.add_parser("run", help="start the dashboard")
    p.add_argument("--host", default="127.0.0.1", help="use 0.0.0.0 to reach it from your home network")
    p.add_argument("--port", type=int, default=5000)
    p.set_defaults(func=cmd_run)
    p = sub.add_parser("demo", help="start the dashboard with live video processing")
    p.add_argument("--video", help="local video file to loop (default: a fall clip from test_footage)")
    p.add_argument("--patient", default="P001", help="person the fall alerts are about (default P001, the sample person)")
    p.add_argument("--no-lstm", action="store_true", help="heuristic only (the LSTM is used by default if it loads)")
    p.add_argument("--no-objects", action="store_true", help="turn off object detection")
    p.add_argument("--no-gait", action="store_true", help="turn off the gait risk score (it never affects fall alerts)")
    p.add_argument("--object-model", default=None, help="YOLO weights (default: the one realtime_fall_detection.py uses)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5000)
    p.set_defaults(func=cmd_demo)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.db = args.db or config.default_database()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
