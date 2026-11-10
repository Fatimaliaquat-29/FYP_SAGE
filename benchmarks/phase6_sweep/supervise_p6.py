"""Phase 6 overnight supervisor: parallel training lanes + rescoring after every finished run.

Each lane repeatedly takes the next not-yet-done run from queue.json["lanes"][i] (re-read before every run, so the
plan can be edited while it runs). A run with "wait_for" waits until that file exists (e.g. a dataset build flag).
Per run: 7.5 h cap, poll every 10 min, one resume retry on CUDA OOM / WinError 1455. After each run finishes
(ok or not), score_p6.py then plot_p6.py run (serialised by a lock). Standard library only; detached.
Writes events.log, STATUS.md (appended), train_<RUN>.log, score_p6.log, plot_p6.log.
"""
import csv
import json
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(r"D:\FYP\PROJECT FILES\main")
OUT = ROOT / "benchmarks" / "phase6_sweep"
PY = ROOT / ".venv2" / "Scripts" / "python.exe"
EVENTS = OUT / "events.log"
STATUS = OUT / "STATUS.md"
QUEUE = OUT / "queue.json"
CAP_S = int(7.5 * 3600)
POLL_S = 600
RETRY = re.compile(r"CUDA out of memory|OutOfMemoryError|WinError 1455|paging file is too small", re.I)
LOG_LOCK, SCORE_LOCK, CLAIM_LOCK = threading.Lock(), threading.Lock(), threading.Lock()
CLAIMED = set()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def event(kind, msg):
    line = f"{now()} {kind} {msg}"
    with LOG_LOCK:
        for p in (EVENTS, STATUS):
            with open(p, "a", encoding="utf-8") as f:
                f.write(("- " if p == STATUS else "") + line + "\n")


def rows(name):
    rc = OUT / "runs" / name / "results.csv"
    return list(csv.DictReader(open(rc, encoding="utf-8"))) if rc.exists() else []


def progress(name):
    rr = rows(name)
    if not rr:
        return "no results.csv yet"
    r = {k.strip(): v.strip() for k, v in rr[-1].items()}
    keys = ["epoch", "train/box_loss", "val/box_loss", "metrics/mAP50(B)", "metrics/mAP50-95(B)"]
    return "; ".join(f"{k}={r.get(k, '?')}" for k in keys)


def done(name):
    return (OUT / "runs" / name / "weights" / "best.pt").exists() and (OUT / f"DONE_{name}").exists()


def launch(cmd, log):
    logf = open(log, "a", encoding="utf-8", errors="replace")
    logf.write(f"\n===== {now()} launch {' '.join(cmd)} =====\n")
    logf.flush()
    p = subprocess.Popen(cmd, cwd=str(OUT), stdout=logf, stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    return p, logf, log.stat().st_size


def train(name):
    log = OUT / f"train_{name}.log"
    cmd = [str(PY), "-u", str(OUT / "train_p6.py"), name]
    t0, retried = time.time(), False
    p, logf, off = launch(cmd, log)
    event("START", f"train {name} pid={p.pid}")
    last = time.time()
    while True:
        rc = p.poll()
        if rc is None:
            if time.time() - t0 > CAP_S:
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
                logf.close()
                event("CAP", f"{name}: cap reached; killed. Last: {progress(name)}")
                return 3
            if time.time() - last >= POLL_S:
                event("PROGRESS", f"{name}: {int((time.time() - t0) / 60)} min; {progress(name)}")
                last = time.time()
            time.sleep(30)
            continue
        logf.close()
        run = OUT / "runs" / name
        if rc == 0 and (run / "weights" / "best.pt").exists():
            (OUT / f"DONE_{name}").write_text(now(), encoding="utf-8")
            event("DONE", f"train {name} exit 0 after {int((time.time() - t0) / 60)} min; {progress(name)}")
            return 0
        tail = log.read_text(encoding="utf-8", errors="replace")[off:]
        last_lines = " | ".join(l.strip() for l in tail.strip().splitlines()[-3:])[:600]
        if RETRY.search(tail) and not retried and (run / "weights" / "last.pt").exists():
            retried = True
            event("RETRY_RESUME", f"{name}: exit {rc}; resuming once. {last_lines}")
            p, logf, off = launch(cmd + ["--resume"], log)
            continue
        event("FAILED", f"train {name} exit {rc}. Last lines: {last_lines}")
        (OUT / f"FAILED_{name}").write_text(now(), encoding="utf-8")
        return 1


def score_and_plot(trigger):
    with SCORE_LOCK:
        for script in ("score_p6.py", "plot_p6.py"):
            if not (OUT / script).exists():
                event("SKIP", f"{script} not found (after {trigger})")
                continue
            p, logf, _ = launch([str(PY), "-u", str(OUT / script)], OUT / script.replace(".py", ".log"))
            rc = p.wait()
            logf.close()
            event("DONE" if rc == 0 else "FAILED", f"{script} exit {rc} (after {trigger})")


def next_run(lane):
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    for item in q["lanes"][lane]:
        name = item["run"]
        with CLAIM_LOCK:
            if name in CLAIMED or done(name) or (OUT / f"FAILED_{name}").exists():
                continue
            CLAIMED.add(name)
        return item
    return None


def lane_worker(lane):
    while True:
        item = next_run(lane)
        if item is None:
            event("LANE_END", f"lane {lane}")
            return
        w = item.get("wait_for")
        if w:
            t0 = time.time()
            while not Path(w).exists():
                if time.time() - t0 > 3 * 3600:
                    event("SKIP", f"{item['run']}: waited 3 h for {w}")
                    break
                time.sleep(60)
            if not Path(w).exists():
                continue
        if item.get("after"):            # start only after another run has finished (GPU memory)
            while not (done(item["after"]) or (OUT / f"FAILED_{item['after']}").exists()):
                time.sleep(60)
        train(item["run"])
        score_and_plot(item["run"])


def main():
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"\n## Supervisor started {now()}\n")
    n = len(json.loads(QUEUE.read_text(encoding="utf-8"))["lanes"])
    ts = []
    for i in range(n):
        t = threading.Thread(target=lane_worker, args=(i,))
        t.start()
        ts.append(t)
        time.sleep(90)            # stagger starts so dataset scans / CUDA init don't collide
    for t in ts:
        t.join()
    event("PIPELINE_END", "all lanes finished")


if __name__ == "__main__":
    sys.exit(main())
