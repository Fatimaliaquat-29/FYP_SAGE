"""Phase 5 overnight pipeline: train C, then train B, then score (score_v8.py) and plot (plot_v8.py).

Standard library only; runs detached so it survives the Claude session ending. Per training run: poll every
10 min, 7 h wall-clock cap, one resume retry on CUDA OOM / WinError 1455 only (same rule as phase 4).
Writes OUT/pipeline_events.log, OUT/STATUS.md (appended), OUT/train_<X>.log, OUT/score_v8.log, OUT/plot_v8.log.
"""
import csv
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase5_v8"
PY = ROOT / ".venv2" / "Scripts" / "python.exe"
EVENTS = OUT / "pipeline_events.log"
STATUS = OUT / "STATUS.md"
CAP_S = 7 * 3600
POLL_S = 600
RETRY_PATTERNS = re.compile(r"CUDA out of memory|OutOfMemoryError|WinError 1455|paging file is too small", re.I)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def event(kind, msg):
    line = f"{now()} {kind} {msg}"
    for p in (EVENTS, STATUS):
        with open(p, "a", encoding="utf-8") as f:
            f.write(("- " if p == STATUS else "") + line + "\n")


def progress(name):
    rc = OUT / "runs" / name / "results.csv"
    if not rc.exists():
        return "no results.csv yet"
    rows = list(csv.DictReader(open(rc, encoding="utf-8")))
    if not rows:
        return "results.csv empty"
    r = {k.strip(): v.strip() for k, v in rows[-1].items()}
    keys = ["epoch", "train/box_loss", "val/box_loss", "metrics/mAP50(B)", "metrics/mAP50-95(B)"]
    return "; ".join(f"{k}={r.get(k, '?')}" for k in keys) + f" ({len(rows)}/30)"


def launch(cmd, log):
    logf = open(log, "a", encoding="utf-8", errors="replace")
    logf.write(f"\n===== {now()} launch {' '.join(cmd)} =====\n")
    logf.flush()
    p = subprocess.Popen(cmd, cwd=str(OUT), stdout=logf, stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    return p, logf, log.stat().st_size


def train(name):
    run = OUT / "runs" / name
    if (run / "weights" / "best.pt").exists() and (run / "results.csv").exists() and \
            len(list(csv.DictReader(open(run / "results.csv", encoding="utf-8")))) >= 30:
        event("SKIP", f"{name} already trained")
        return 0
    log = OUT / f"train_{name}.log"
    cmd = [str(PY), "-u", str(OUT / "train_v8.py"), name]
    t0, retried = time.time(), False
    p, logf, offset = launch(cmd, log)
    event("START", f"train {name} pid={p.pid} cap=7h")
    last = time.time()
    while True:
        rc = p.poll()
        if rc is None:
            if time.time() - t0 > CAP_S:
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
                logf.close()
                event("CAP", f"{name}: 7 h cap reached; killed. Last: {progress(name)}")
                return 3
            if time.time() - last >= POLL_S:
                event("PROGRESS", f"{name}: {int((time.time() - t0) / 60)} min; {progress(name)}")
                last = time.time()
            time.sleep(30)
            continue
        logf.close()
        if rc == 0 and (run / "weights" / "best.pt").exists():
            event("DONE", f"train {name} exit 0 after {int((time.time() - t0) / 60)} min; {progress(name)}")
            return 0
        tail = log.read_text(encoding="utf-8", errors="replace")[offset:]
        last_lines = " | ".join(l.strip() for l in tail.strip().splitlines()[-3:])[:600]
        if RETRY_PATTERNS.search(tail) and not retried and (run / "weights" / "last.pt").exists():
            retried = True
            event("RETRY_RESUME", f"{name}: exit {rc}, OOM/WinError1455; resuming once. {last_lines}")
            p, logf, offset = launch(cmd + ["--resume"], log)
            continue
        event("FAILED", f"train {name} exit {rc}. Last lines: {last_lines}")
        return 1


def run_step(script, log):
    if not (OUT / script).exists():
        event("SKIP", f"{script} not found")
        return 1
    p, logf, _ = launch([str(PY), "-u", str(OUT / script)], OUT / log)
    rc = p.wait()
    logf.close()
    event("DONE" if rc == 0 else "FAILED", f"{script} exit {rc}")
    return rc


def main():
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"\n## Overnight pipeline (started {now()})\n")
    rc_c = train("C")
    rc_b = train("B")
    run_step("score_v8.py", "score_v8.log")
    run_step("plot_v8.py", "plot_v8.log")
    event("PIPELINE_END", f"C rc={rc_c}, B rc={rc_b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
