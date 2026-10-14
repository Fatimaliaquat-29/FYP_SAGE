"""Overnight driver. Runs every stage as a subprocess (venv python, -B), sequentially in stage order, with a
per-stage cap and a 12 h overall budget. State in state.json (resumable), progress in STATUS.md,
timestamped log in driver.log (stdout of this process). Launch detached via launch_driver.py."""
import ctypes
import datetime as dt
import os
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, RAW, LOGS, RUNS, PY, log, write_json, read_json, decision, run_start, now, BUDGET_H

STATE = OUT / "state.json"
PIDFILE = OUT / "driver.pid"
ENV = os.environ.copy()
ENV.update(PYTHONDONTWRITEBYTECODE="1", TF_CPP_MIN_LOG_LEVEL="2", YOLO_AUTOINSTALL="False",
           PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
DEADLINE = run_start() + dt.timedelta(hours=BUDGET_H)
FINAL_RESERVE_S = 15 * 60   # always keep this much for the report


# ---------------------------------------------------------------------------------------------
def sleep_guard():
    ES = 0x80000000 | 0x00000001 | 0x00000002   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    while True:
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES)
        except Exception as e:
            log(f"sleep guard error {e!r}")
        time.sleep(60)


def pid_alive(pid):
    try:
        import psutil
        return psutil.pid_exists(pid) and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
    except Exception:
        return False


def kill_tree(pid):
    subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)


def remaining_s():
    return (DEADLINE - now()).total_seconds()


# ---------------------------------------------------------------------------------------------
class Driver:
    def __init__(self):
        self.st = read_json(STATE, None) or {"run_start": run_start().isoformat(), "driver_launches": [], "stages": {}}
        self.st["driver_launches"].append(now().isoformat(timespec="seconds"))
        self.save()

    def save(self):
        write_json(STATE, self.st)
        self.write_status()

    def stage(self, name):
        return self.st["stages"].setdefault(name, {"status": "pending"})

    def write_status(self, extra=""):
        lines = ["# Overnight run -- STATUS", "",
                 f"- updated: {now():%Y-%m-%d %H:%M:%S}",
                 f"- run start: {run_start():%Y-%m-%d %H:%M}  |  elapsed: {(now() - run_start()).total_seconds() / 3600:.2f} h  |  "
                 f"budget ends {DEADLINE:%H:%M} ({remaining_s() / 3600:.2f} h left)", "",
                 "| stage | status | start | end | minutes | note |", "|---|---|---|---|---|---|"]
        for k, v in self.st["stages"].items():
            s, e = v.get("start"), v.get("end")
            mins = ""
            if s:
                t1 = dt.datetime.fromisoformat(e) if e else now()
                mins = f"{(t1 - dt.datetime.fromisoformat(s)).total_seconds() / 60:.1f}"
            lines.append(f"| {k} | {v.get('status')} | {(s or '')[11:19]} | {(e or '')[11:19]} | {mins} | {v.get('note', '')} |")
        for key in ("B_yolo26n_30ep", "C_yolo26n_50ep"):
            eps = read_json(RAW / f"train_{key}_epochs.json", [])
            if eps:
                last = eps[-1]
                m = last.get("metrics", {})
                lines.append("")
                lines.append(f"- {key}: {len(eps)} epoch records; last epoch {last['epoch']} took "
                             f"{(last.get('duration_s') or 0):.0f}s; mAP50={m.get('metrics/mAP50(B)', float('nan')):.4f} "
                             f"mAP50-95={m.get('metrics/mAP50-95(B)', float('nan')):.4f}")
        if extra:
            lines += ["", extra]
        (OUT / "STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- generic subprocess stage ----
    def run(self, name, script_args, cap_min, logname=None, min_needed_min=1, reserve=True):
        sd = self.stage(name)
        if sd["status"] in ("done", "failed", "timeout", "skipped", "partial"):
            log(f"{name}: already {sd['status']}, skipping")
            return sd["status"]
        if sd["status"] == "running" and sd.get("pid") and pid_alive(sd["pid"]):
            log(f"{name}: re-attaching to live pid {sd['pid']}")
            return self._wait(name, sd, None, cap_min, reserve=reserve)
        avail = remaining_s() - (FINAL_RESERVE_S if reserve else 0)
        if avail < min_needed_min * 60:
            sd.update(status="skipped", note=f"budget: {avail / 60:.0f} min left < {min_needed_min} needed", end=now().isoformat(timespec="seconds"))
            self.save()
            log(f"{name}: SKIPPED for budget")
            return "skipped"
        logf = LOGS / f"{logname or name}.log"
        fh = open(logf, "a", encoding="utf-8")
        fh.write(f"\n===== {now():%Y-%m-%d %H:%M:%S} {name}: {' '.join(map(str, script_args))}\n")
        fh.flush()
        p = subprocess.Popen([str(PY), "-B", *map(str, script_args)], cwd=str(OUT), stdout=fh, stderr=subprocess.STDOUT,
                             stdin=subprocess.DEVNULL, env=ENV)
        sd.update(status="running", pid=p.pid, start=sd.get("start") or now().isoformat(timespec="seconds"),
                  log=str(logf), cmd=list(map(str, script_args)))
        self.save()
        log(f"{name}: started pid {p.pid} (cap {cap_min} min) -> {logf.name}")
        return self._wait(name, sd, p, cap_min, fh, reserve=reserve)

    def _wait(self, name, sd, p, cap_min, fh=None, reserve=True):
        t0 = dt.datetime.fromisoformat(sd["start"])
        last_hb = time.time()
        timed_out = None
        while True:
            rc = p.poll() if p is not None else (None if pid_alive(sd["pid"]) else -999)
            if rc is not None:
                break
            el = (now() - t0).total_seconds()
            if el > cap_min * 60:
                timed_out = "stage cap"
            elif remaining_s() < (FINAL_RESERVE_S if reserve else 0):
                timed_out = "overall budget"
            if timed_out:
                log(f"{name}: killing pid {sd['pid']} ({timed_out}; {el / 60:.1f} min)")
                kill_tree(sd["pid"])
                time.sleep(5)
                rc = -1
                break
            if time.time() - last_hb > 300:
                log(f"heartbeat: {name} running {el / 60:.1f} min")
                self.write_status()
                last_hb = time.time()
            time.sleep(15)
        if fh:
            fh.close()
        sd["end"] = now().isoformat(timespec="seconds")
        sd["returncode"] = rc
        if timed_out:
            sd["status"] = "timeout"
            sd["note"] = f"killed: {timed_out} (partial results kept)"
        elif rc == 0:
            sd["status"] = "done"
        else:
            sd["status"] = "failed"
            sd["note"] = f"exit {rc}"
        try:
            tail = Path(sd["log"]).read_text(encoding="utf-8", errors="replace").splitlines()[-25:]
            if sd["status"] != "done":
                sd["log_tail"] = tail
                log(f"{name}: {sd['status'].upper()} rc={rc}. log tail:\n    " + "\n    ".join(tail))
        except Exception:
            pass
        self.save()
        log(f"{name}: {sd['status']} (rc={rc})")
        return sd["status"]

    # ---- training with the crash policy: resume once, then batch 8 ----
    def train(self, name, key, epochs, patience, cap_min):
        sd = self.stage(name)
        if sd["status"] in ("done", "failed", "timeout", "skipped"):
            return sd["status"]
        t_start = dt.datetime.fromisoformat(sd["start"]) if sd.get("start") else now()
        sd.setdefault("attempts", [])
        sd["start"] = t_start.isoformat(timespec="seconds")
        self.save()
        base = ["stage5_train.py", "--key", key]
        order = ["fresh", "resume", "batch8"]
        if sd["attempts"]:
            last = sd["attempts"][-1]
            sub = self.stage(last["sub_stage"])
            if sub.get("status") == "running":
                if sub.get("pid") and pid_alive(sub["pid"]):
                    left = cap_min - (now() - t_start).total_seconds() / 60
                    st = self.run(last["sub_stage"], last["args"], left)     # re-attach to the live trainer
                    if st == "done":
                        sd.update(status="done", end=now().isoformat(timespec="seconds"), note=f"succeeded on attempt {last['kind']}")
                        self.save()
                        return "done"
                    if st == "timeout":
                        sd.update(status="timeout", end=now().isoformat(timespec="seconds"), note="killed by cap/budget")
                        self.save()
                        return "timeout"
                else:
                    sub.update(status="failed", note="process gone at driver relaunch", end=now().isoformat(timespec="seconds"))
                    self.save()
        plan = []
        for kind in order[len(sd["attempts"]):]:
            if kind == "fresh":
                plan.append(("fresh", base + ["--name", key, "--epochs", epochs, "--patience", patience]))
            elif kind == "resume":
                plan.append(("resume", None))
            else:
                plan.append(("batch8", base + ["--name", f"{key}_b8", "--epochs", epochs, "--patience", patience, "--batch", 8]))
        for kind, args in plan:
            left = cap_min - (now() - t_start).total_seconds() / 60
            if left < 10:
                sd.update(status="timeout", note="stage cap reached before/among retries", end=now().isoformat(timespec="seconds"))
                self.save()
                return "timeout"
            if kind == "resume":
                meta = read_json(RAW / f"train_{key}.json", {})
                atts = meta.get("attempts", [])
                last = Path(atts[-1].get("save_dir", "")) / "weights" / "last.pt" if atts and atts[-1].get("save_dir") else None
                if last is None or not last.exists():
                    decision(f"{key}: crash before any last.pt existed, so resume=True was impossible; retrying the identical fresh run once instead.")
                    args = base + ["--name", f"{key}_retry", "--epochs", epochs, "--patience", patience]
                else:
                    args = base + ["--name", key, "--resume", str(last)]
            sub_name = f"{name}__attempt{len(sd['attempts']) + 1}_{kind}"
            sd["attempts"].append({"kind": kind, "args": list(map(str, args)), "sub_stage": sub_name})
            sd["status"] = "running"
            self.save()
            st = self.run(sub_name, args, left, logname=f"{name}_{kind}")
            sd["pid"] = self.stage(sub_name).get("pid")
            if st == "done":
                sd.update(status="done", end=now().isoformat(timespec="seconds"), note=f"succeeded on attempt {kind}")
                if kind != "fresh":
                    decision(f"{key}: training needed retry policy step '{kind}' (see state.json / logs).")
                self.save()
                return "done"
            if st == "timeout":
                sd.update(status="timeout", end=now().isoformat(timespec="seconds"), note=f"killed by cap/budget during {kind}")
                self.save()
                return "timeout"
            log(f"{name}: attempt {kind} ended {st}; applying crash policy")
        sd.update(status="failed", end=now().isoformat(timespec="seconds"), note="all retry steps failed")
        self.save()
        return "failed"


# ---------------------------------------------------------------------------------------------
def main():
    if PIDFILE.exists():
        try:
            old = int(PIDFILE.read_text().strip())
            if old != os.getpid() and pid_alive(old):
                import psutil
                if "python" in psutil.Process(old).name().lower():
                    log(f"another driver (pid {old}) is alive; exiting")
                    return
        except Exception:
            pass
    PIDFILE.write_text(str(os.getpid()))
    threading.Thread(target=sleep_guard, daemon=True).start()
    log(f"driver start pid={os.getpid()} deadline={DEADLINE:%Y-%m-%d %H:%M}")
    D = Driver()
    try:
        D.run("S0_preflight", ["stage0_preflight.py"], 20)
        D.run("S1_control", ["stage1_control.py"], 60)
        D.run("S2_stock", ["score_models.py", "--models", "stock_yolo26n", "stock_yolo26s", "stock_yolov8n", "--confs", "0.4", "0.25"], 30)
        D.run("S3_enhance_A_stock", ["stage3_enhance.py", "--models", "A_v7", "stock_yolo26n", "--grids"], 45)
        t4 = now()
        D.run("S4a_pose_score", ["pose_v2.py", "--part", "score"], 35)
        used = (now() - t4).total_seconds() / 60
        D.run("S4b_pose_speed", ["pose_v2.py", "--part", "speed"], max(10, 75 - used))
        b = D.train("S5_train_B", "B_yolo26n_30ep", 30, 10, 270)
        if b in ("done", "timeout"):
            D.run("S5_score_B", ["score_models.py", "--models", "B_yolo26n_30ep", "--confs", "0.4", "--val"], 45)
        else:
            D.stage("S5_score_B").update(status="skipped", note=f"B training {b}")
            D.save()
        D.run("S6_gate", ["stage6_gate.py"], 5)
        gate = read_json(RAW / "gate.json", {})
        if gate.get("run_C"):
            cap_c = (remaining_s() - FINAL_RESERVE_S - 40 * 60) / 60
            c = D.train("S6_train_C", "C_yolo26n_50ep", 50, 50, cap_c)
            if c in ("done", "timeout"):
                D.run("S6_score_C", ["score_models.py", "--models", "C_yolo26n_50ep", "--confs", "0.4", "--val"], 30)
        else:
            sd = D.stage("S6_train_C")
            if sd["status"] == "pending":
                sd.update(status="skipped", note="C SKIPPED: " + ", ".join(gate.get("failed_conditions", ["gate missing"])))
                D.save()
        models = ["B_yolo26n_30ep"] + (["C_yolo26n_50ep"] if D.stage("S6_train_C").get("status") in ("done", "timeout") else [])
        D.run("S6_enhance_BC", ["stage3_enhance.py", "--models", *models], 45)
    except Exception as e:
        log(f"DRIVER ERROR: {e!r}\n{traceback.format_exc()}")
        D.st["driver_error"] = traceback.format_exc()[-3000:]
        D.save()
    # report always runs (it tolerates missing inputs)
    sd = D.stage("S7_report")
    sd["status"] = "pending"
    D.run("S7_report", ["report.py"], 20, min_needed_min=0, reserve=False)
    D.st["finished"] = now().isoformat(timespec="seconds")
    D.save()
    log(f"driver finished. RESULTS: {OUT / 'RESULTS.md'}")
    PIDFILE.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
