"""Launch overnight_driver.py fully detached (survives this session). stdout/stderr -> driver.log (append)."""
import os
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
PY = Path(r"D:\FYP\PROJECT FILES\fatima\.venv2\Scripts\python.exe")
DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP, CREATE_BREAKAWAY_FROM_JOB = 0x8, 0x200, 0x01000000

env = os.environ.copy()
env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8",
           TF_CPP_MIN_LOG_LEVEL="2", YOLO_AUTOINSTALL="False")
log = open(OUT / "driver.log", "a", encoding="utf-8")
args = [str(PY), "-B", str(OUT / "overnight_driver.py")]
for flags in (DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB,
              DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP):
    try:
        p = subprocess.Popen(args, cwd=str(OUT), stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             env=env, creationflags=flags, close_fds=True)
        print(f"launched pid {p.pid} flags={hex(flags)}")
        break
    except OSError as e:
        print(f"flags {hex(flags)} failed: {e}")
else:
    sys.exit(1)
