"""A4 supervisor: launch train_A2.py, poll every 10 min, enforce the 6 h cap, one resume retry.

Standard library only. Writes:
  OUT/train_A2.log            training stdout+stderr (all attempts, appended)
  OUT/supervisor_events.log   one line per event (PROGRESS / RETRY_RESUME / DONE / FAILED / CAP)
  OUT/STATUS.md               progress lines appended under "## A4 training progress"
Exit codes: 0 done (best.pt exists), 1 failed, 2 failed after retry, 3 wall-clock cap hit.

Retry rule (phase-3 prompt): on CUDA OOM or WinError 1455 only, retry ONCE with the same
settings via resume=True. No hyperparameter changes. Anything else: stop and report.
"""
import csv
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase3_a2"
PY = ROOT / ".venv2" / "Scripts" / "python.exe"
LOG = OUT / "train_A2.log"
EVENTS = OUT / "supervisor_events.log"
STATUS = OUT / "STATUS.md"
RUN = OUT / "runs" / "A2"
CAP_S = 6 * 3600
POLL_S = 600
RETRY_PATTERNS = re.compile(r"CUDA out of memory|OutOfMemoryError|WinError 1455|paging file is too small", re.I)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def event(kind, msg):
    line = f"{now()} {kind} {msg}"
    with open(EVENTS, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"- {line}\n")


def progress():
    rc = RUN / "results.csv"
    if not rc.exists():
        return "no results.csv yet (epoch 1 not finished)"
    rows = list(csv.DictReader(open(rc, encoding="utf-8")))
    if not rows:
        return "results.csv empty"
    r = {k.strip(): v.strip() for k, v in rows[-1].items()}
    keys = ["epoch", "train/box_loss", "train/cls_loss", "val/box_loss", "metrics/mAP50(B)", "metrics/mAP50-95(B)"]
    return "; ".join(f"{k}={r.get(k, '?')}" for k in keys) + f" ({len(rows)}/30 epochs logged)"


def launch(resume):
    cmd = [str(PY), "-u", str(OUT / "train_A2.py")] + (["--resume"] if resume else [])
    logf = open(LOG, "a", encoding="utf-8", errors="replace")
    logf.write(f"\n===== {now()} launch {' '.join(cmd)} =====\n")
    logf.flush()
    p = subprocess.Popen(cmd, cwd=str(OUT), stdout=logf, stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    return p, logf, LOG.stat().st_size


def kill_tree(pid):
    subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)


def main():
    t0 = time.time()
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write("\n## A4 training progress\n")
    retried = False
    p, logf, offset = launch(resume=False)
    event("START", f"pid={p.pid} cap=6h poll=10min")
    last_poll = time.time()
    while True:
        rc = p.poll()
        if rc is None:
            if time.time() - t0 > CAP_S:
                kill_tree(p.pid)
                logf.close()
                event("CAP", f"6 h wall-clock cap reached; training killed. Last: {progress()}")
                return 3
            if time.time() - last_poll >= POLL_S:
                event("PROGRESS", f"elapsed {int((time.time() - t0) / 60)} min; {progress()}")
                last_poll = time.time()
            time.sleep(30)
            continue
        logf.close()
        if rc == 0 and (RUN / "weights" / "best.pt").exists():
            event("DONE", f"exit 0 after {int((time.time() - t0) / 60)} min; {progress()}")
            return 0
        tail = LOG.read_text(encoding="utf-8", errors="replace")[offset:]
        retryable = bool(RETRY_PATTERNS.search(tail))
        last_lines = " | ".join(l.strip() for l in tail.strip().splitlines()[-3:])[:600]
        if retryable and not retried and (RUN / "weights" / "last.pt").exists():
            retried = True
            event("RETRY_RESUME", f"exit {rc}, OOM/WinError1455 detected; resuming once. Last lines: {last_lines}")
            p, logf, offset = launch(resume=True)
            continue
        why = ("retryable error but no last.pt to resume from" if retryable and not retried
               else "second failure" if retried else "non-retryable error")
        event("FAILED", f"exit {rc} ({why}). Last lines: {last_lines}")
        return 2 if retried else 1


if __name__ == "__main__":
    sys.exit(main())
