"""Turns stored records into plain, kind language for a family caregiver.

Kept separate from the routes so the pages and the JSON API word things
the same way. Nothing here should use technical words on screen.
"""

import json
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from . import queries
from .sources import GAIT_HIGH_FROM, GAIT_MEDIUM_FROM

SEVERITY_LABELS = {"high": "Urgent", "medium": "Worth a look", "low": "For information"}
TYPE_LABELS = {"fall": "Possible fall", "gait_risk": "Walking"}
TYPE_FILTER_LABELS = {"fall": "Possible falls", "gait_risk": "Walking"}
WALK_LEVEL_LABELS = {"low": "Steady", "medium": "A little unsteady", "high": "Unsteady"}
GAIT_TITLES = {
    "low": "Walking looked steady",
    "medium": "Walking looked a little unsteady",
    "high": "Walking looked unsteady",
}
# The legend: what each level means and what to do about it.
LEVELS = [
    {"severity": "high", "label": "Urgent",
     "means": "Something may have gone wrong, such as a possible fall.",
     "do": "Check on them straight away."},
    {"severity": "medium", "label": "Worth a look",
     "means": "Not an emergency, but something has changed, such as less steady walking.",
     "do": "Have a look when you have a moment."},
    {"severity": "low", "label": "For information",
     "means": "Just keeping you up to date.",
     "do": "Nothing to do."},
]
TREND_RANGES = {"7": 7, "30": 30, "90": 90, "all": None}
TREND_RANGE_LABELS = {"7": "7 days", "30": "30 days", "90": "90 days", "all": "All time"}
DEFAULT_TREND_RANGE = "30"
ROLE_LABELS = {"caregiver": "Family or carer", "admin": "Manager"}
ROLE_HELP = {
    "caregiver": "Can see everything and mark things as checked.",
    "admin": "Can also add results and choose who can sign in.",
}


class FilterError(ValueError):
    pass


def get_tz(name):
    """None means the device's own time zone."""
    if not name:
        return datetime.now().astimezone().tzinfo
    if name.upper() == "UTC":
        return timezone.utc
    return ZoneInfo(name)


def now_utc():
    return datetime.now(timezone.utc)


# --- time --------------------------------------------------------------------

def format_clock(dt):
    hour = dt.hour % 12 or 12
    return f"{hour}:{dt.minute:02d} {'am' if dt.hour < 12 else 'pm'}"


def format_day(dt, today):
    if dt.date() == today:
        return "Today"
    if dt.date() == today - timedelta(days=1):
        return "Yesterday"
    if dt.year == today.year:
        return f"{dt:%a} {dt.day} {dt:%b}"
    return f"{dt.day} {dt:%b %Y}"


def format_short_date(dt):
    return f"{dt.day} {dt:%b %Y}"


def local(utc_string, tz):
    return queries.parse_utc_string(utc_string).astimezone(tz)


def when_label(utc_string, tz):
    """e.g. "today at 3:42 pm", "Mon 2 Nov at 9:05 am"."""
    when = local(utc_string, tz)
    day = format_day(when, now_utc().astimezone(tz).date())
    if day in ("Today", "Yesterday"):
        day = day.lower()
    return f"{day} at {format_clock(when)}"


def clock_now(tz):
    return format_clock(now_utc().astimezone(tz))


# --- people ------------------------------------------------------------------

def call_name(row):
    """What to call the person in sentences: preferred name, else first name."""
    return row["preferred_name"] or row["name"].split()[0]


def present_patient(row):
    return {"id": row["id"], "external_id": row["external_id"], "name": row["name"],
            "call_name": call_name(row), "preferred_name": row["preferred_name"],
            "age": row["age"], "room": row["room"]}


# --- events ------------------------------------------------------------------

def confidence_label(value):
    if value >= 0.85:
        return "Very sure"
    if value >= 0.6:
        return "Fairly sure"
    return "Not very sure"


def event_title(row):
    if row["type"] == "fall":
        return "Possible fall"
    return GAIT_TITLES[row["severity"]]


def event_description(row, name):
    if row["description"]:
        return row["description"]
    if row["type"] == "fall":
        if row["severity"] == "low":
            return "The camera saw a movement that might have been a fall, but it was not sure."
        return f"The camera saw a movement that looked like a fall. Please make sure {name} is all right."
    if row["severity"] == "high":
        return (f"{name}'s walking looked unsteady, so the chance of a fall is higher than "
                f"we would like. A chat with {name} or their doctor may help.")
    if row["severity"] == "medium":
        return f"{name} walked a little less steadily than usual."
    return f"{name}'s walking looked steady."


def present_event(row, patient_row, tz, today=None):
    name = call_name(patient_row)
    when = local(row["occurred_at"], tz)
    today = today or now_utc().astimezone(tz).date()
    title = event_title(row)
    checked = row["checked_at"] is not None
    keys = row.keys()
    checked_by = row["checked_by_name"] if "checked_by_name" in keys else None
    checked_label = None
    if checked:
        checked_label = f"Checked {when_label(row['checked_at'], tz)}"
        if checked_by:
            checked_label = f"Checked by {checked_by}, {when_label(row['checked_at'], tz)}"
    try:
        details = json.loads(row["details_json"] or "{}")
    except ValueError:
        details = {}
    return {
        "id": row["id"],
        "type": row["type"],
        "type_label": TYPE_LABELS[row["type"]],
        "severity": row["severity"],
        "severity_label": SEVERITY_LABELS[row["severity"]],
        "title": title,
        "headline": f"{title} at {format_clock(when)}",
        "day_label": format_day(when, today),
        "time_label": format_clock(when),
        "occurred_at": row["occurred_at"],
        "occurred_at_local": when.isoformat(),
        "description": event_description(row, name),
        "confidence": row["confidence"],
        "confidence_label": confidence_label(row["confidence"]),
        "risk_score": row["risk_score"],
        "walk_label": WALK_LEVEL_LABELS[row["severity"]] if row["type"] == "gait_risk" else None,
        "source": row["source"],
        "checked": checked,
        "checked_label": checked_label,
        "needs_check": not checked and row["severity"] in queries.ATTENTION_SEVERITIES,
        "call_name": name,
        "details": details,
    }


def present_status(summary, tz):
    last = summary["last_event"]
    last_label = None
    if last is not None:
        when = local(last["occurred_at"], tz)
        last_label = f"{format_day(when, now_utc().astimezone(tz).date())} at {format_clock(when)}"
    n = summary["open_alerts"]
    if n:
        state, label = "attention", "Needs your attention"
        detail = f"{n} {'thing' if n == 1 else 'things'} to check"
    elif last is None:
        state, label, detail = "none", "No news yet", "Nothing has been seen so far"
    else:
        state, label, detail = "ok", "All is well", "Nothing needs checking"
    return {"state": state, "label": label, "detail": detail, "open_alerts": n,
            "urgent": summary.get("urgent", 0),
            "last_event_label": last_label,
            "last_event_at": last["occurred_at"] if last is not None else None}


def glance(patient, status):
    """The one-glance answer at the top: is everything okay, and what do I do?"""
    name = patient["call_name"]
    check_button = f"Then press “I’ve checked on {name}” below, so everyone knows it has been seen."
    if status["urgent"]:
        return {"state": "urgent",
                "headline": f"{name} may need you now.",
                "intro": "Here is what to do:",
                "steps": [f"Check on {name} straight away: go and see them, or give them a call.",
                          "If they are hurt or unwell, call for help.",
                          check_button]}
    if status["open_alerts"]:
        return {"state": "attention",
                "headline": "Nothing urgent, but something is worth a look.",
                "intro": "When you have a moment:",
                "steps": ["Read the note below.",
                          f"If you are unsure, have a chat with {name} or their doctor.",
                          check_button]}
    if status["state"] == "none":
        return {"state": "none",
                "headline": f"No news about {name} yet.",
                "intro": "Nothing has been seen so far. Updates will appear here by themselves.",
                "steps": []}
    return {"state": "ok",
            "headline": f"All is well with {name}.",
            "intro": "There is nothing you need to do right now.",
            "steps": []}


def glance_everyone(people):
    needing = [p for p in people if p["status"]["open_alerts"]]
    urgent = [p for p in people if p["status"]["urgent"]]
    if urgent:
        names = ", ".join(p["call_name"] for p in urgent)
        return {"state": "urgent", "headline": f"{names} may need you now.",
                "intro": "Open their page below to see what to do."}
    if needing:
        names = ", ".join(p["call_name"] for p in needing)
        return {"state": "attention", "headline": f"Something is worth a look for {names}.",
                "intro": "Nothing urgent. Open their page below when you have a moment."}
    return {"state": "ok", "headline": "All is well with everyone.",
            "intro": "There is nothing you need to do right now."}


# --- filters -----------------------------------------------------------------

def _choices(raw, allowed, what):
    if raw is None or raw.strip() in ("", "all"):
        return None
    values = [v.strip() for v in raw.split(",") if v.strip()]
    bad = [v for v in values if v not in allowed]
    if bad:
        raise FilterError(f"Unknown {what}: {', '.join(bad)}")
    return values


def _date(raw, what):
    if raw is None or not raw.strip():
        return None
    try:
        return date.fromisoformat(raw.strip())
    except ValueError:
        raise FilterError(f"The {what} date should look like 2026-11-02") from None


def parse_filters(args, tz):
    """Read type/severity/from/to query arguments.

    Returns (filters for queries.query_events, values to echo back into the form).
    Dates are whole local days; `to` includes the whole of that day.
    """
    types = _choices(args.get("type"), queries.EVENT_TYPES, "event type")
    severities = _choices(args.get("severity"), queries.SEVERITIES, "severity")
    start_day = _date(args.get("from"), "start")
    end_day = _date(args.get("to"), "end")
    if start_day and end_day and start_day > end_day:
        raise FilterError("The start date is after the end date")
    filters = {"types": types, "severities": severities, "start": None, "end": None}
    if start_day:
        filters["start"] = queries.to_utc_string(datetime.combine(start_day, time(), tz))
    if end_day:
        filters["end"] = queries.to_utc_string(
            datetime.combine(end_day + timedelta(days=1), time(), tz))
    form = {"type": ",".join(types or []), "severity": ",".join(severities or []),
            "from": start_day.isoformat() if start_day else "",
            "to": end_day.isoformat() if end_day else ""}
    return filters, form


def parse_page(raw):
    try:
        page = int(raw or 1)
    except ValueError:
        raise FilterError("The page number should be a whole number") from None
    if page < 1:
        raise FilterError("The page number should be 1 or more")
    return page


# --- walking trend -----------------------------------------------------------

def parse_trend_range(raw):
    raw = (raw or DEFAULT_TREND_RANGE).strip()
    if raw not in TREND_RANGES:
        raise FilterError(f"Unknown range: {raw}. Use one of {', '.join(TREND_RANGES)}")
    return raw


def trend_start(range_key, now=None):
    days = TREND_RANGES[range_key]
    if days is None:
        return None
    return queries.to_utc_string((now or now_utc()) - timedelta(days=days))


# Chart drawing area in SVG user units. The SVG stretches to its box
# (preserveAspectRatio="none"); strokes use non-scaling-stroke so lines and
# dots keep their size at any width.
CHART_W, CHART_H = 1000, 300
BAND_MEDIUM_Y = round((1 - GAIT_MEDIUM_FROM) * CHART_H, 1)
BAND_HIGH_Y = round((1 - GAIT_HIGH_FROM) * CHART_H, 1)


def build_trend_chart(rows, tz, range_key, name, now=None):
    now = now or now_utc()
    if not rows:
        return {"points": [], "path": "", "x_labels": [], "summary": None, "rows": []}
    times = [queries.parse_utc_string(r["occurred_at"]) for r in rows]
    days = TREND_RANGES[range_key]
    if days is None:
        t0, t1 = times[0], times[-1]
    else:
        t0, t1 = now - timedelta(days=days), now
    span = (t1 - t0).total_seconds()

    points, table = [], []
    for r, t in zip(rows, times):
        frac = 0.5 if span <= 0 else min(max((t - t0).total_seconds() / span, 0.0), 1.0)
        points.append({"x": round(frac * CHART_W, 1), "y": round((1 - r["risk_score"]) * CHART_H, 1)})
        when = t.astimezone(tz)
        table.append({"date": f"{format_short_date(when)}, {format_clock(when)}",
                      "level": WALK_LEVEL_LABELS[r["severity"]]})
    path = "M" + " L".join(f"{p['x']} {p['y']}" for p in points)

    start_label = format_short_date(t0.astimezone(tz))
    end_label = "Today" if days is not None else format_short_date(t1.astimezone(tz))
    x_labels = [start_label, end_label] if start_label != end_label else [start_label]

    n = len(rows)
    first, latest = rows[0]["risk_score"], rows[-1]["risk_score"]
    summary = (f"{name} was seen walking {n} {'time' if n == 1 else 'times'}. "
               f"The most recent walk looked {WALK_LEVEL_LABELS[rows[-1]['severity']].lower()} "
               f"({table[-1]['date']}).")
    if n > 1:
        if latest < first - 0.05:
            summary += " Walking looks steadier than at the start of this period."
        elif latest > first + 0.05:
            summary += " Walking looks less steady than at the start of this period."
        else:
            summary += " Walking looks about the same as at the start of this period."
    return {"points": points, "path": path, "x_labels": x_labels, "summary": summary, "rows": table}
