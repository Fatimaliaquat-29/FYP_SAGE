"""Shared paths/helpers for the overnight YOLO26 experiments. Everything written goes under OUT."""
import datetime as _dt
import importlib.util
import json
import logging
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # never drop __pycache__ into ROOT/src when importing project modules

ROOT = Path(r"D:\FYP\PROJECT FILES\fatima")
OUT = ROOT / "benchmarks" / "overnight_yolo26"
RAW = OUT / "raw"
LOGS = OUT / "logs"
EVALSETS = OUT / "evalsets" / "held_out"   # 'held_out' component => footage_paths guard treats it as protected
WEIGHTS = OUT / "weights"
RUNS = OUT / "runs"
PY = ROOT / ".venv2" / "Scripts" / "python.exe"
for _d in (RAW, LOGS, EVALSETS, WEIGHTS, RUNS):
    _d.mkdir(parents=True, exist_ok=True)

# Run start = when the overnight task began (git branch creation, 2026-10-10 01:47:00 local).
RUN_START_ISO = "2026-10-10T01:47:00"
BUDGET_H = 12.0

CONF = 0.4
CONF_LOW = 0.25
IMGSZ = 640
IOUS = (0.5, 0.3)

MODELS = {
    "A_v7": ROOT / "models" / "yolov8n_sage_merged_v7.pt",
    "v6": ROOT / "models" / "yolov8n_sage_merged_v6.pt",
    "stock_yolo26n": ROOT / "yolo26n.pt",
    "stock_yolo26s": WEIGHTS / "yolo26s.pt",
    "stock_yolov8n": ROOT / "models" / "yolov8n.pt",
    "B_yolo26n_30ep": RUNS / "B_yolo26n_30ep" / "weights" / "best.pt",
    "C_yolo26n_50ep": RUNS / "C_yolo26n_50ep" / "weights" / "best.pt",
}
STOCK = {"stock_yolo26n", "stock_yolo26s", "stock_yolov8n"}


def model_path(key):
    """B/C may land in a different run dir after a crash fallback; the trainer records the real best.pt."""
    meta = RAW / f"train_{key}.json"
    if meta.exists():
        best = json.loads(meta.read_text(encoding="utf-8")).get("best_pt")
        if best:
            return Path(best)
    return MODELS[key]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def now():
    return _dt.datetime.now()


def run_start():
    return _dt.datetime.fromisoformat(RUN_START_ISO)


def elapsed_h():
    return (now() - run_start()).total_seconds() / 3600.0


def log(msg):
    print(f"[{now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, default=_json_default), encoding="utf-8")
    os.replace(tmp, path)


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _json_default(o):
    try:
        import numpy as np
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return None if np.isnan(o) else float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, float) and o != o:
        return None
    raise TypeError(f"not serialisable: {type(o)}")


def decision(text):
    """Append a decision + reason to DECISIONS.md (never rewritten, only appended)."""
    with open(OUT / "DECISIONS.md", "a", encoding="utf-8") as f:
        f.write(f"- [{now():%Y-%m-%d %H:%M}] {text}\n")


def import_by_path(name, path):
    """Import a project module from its file path without writing bytecode into ROOT."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def silence_pipeline_logger():
    """pipeline_utils attaches a FileHandler to data/detections.log at import time unless the
    'posture_pipeline' logger already has a handler. Pre-attach a NullHandler so importing it
    never opens (or appends to) that existing file."""
    lg = logging.getLogger("posture_pipeline")
    if not lg.handlers:
        lg.addHandler(logging.NullHandler())
    lg.propagate = False
    lg.setLevel(logging.CRITICAL + 1)


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def fmt_rate(k, n):
    return "--" if not n else f"{k}/{n} = {k / n:.3f}"
