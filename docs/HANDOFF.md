# S.A.G.E. project handoff: where everything is

The project lives in two places. You need both.

| | What it holds | Where |
|---|---|---|
| **Git repo** | Code (`src/`, `tests/`, root scripts), hand-drawn labels (`handlabels/*/labels`, `eval/*/labels`), docs, small reports and result tables, the small model checkpoints already tracked in `models/` | https://github.com/Fatimaliaquat-29/FYP_SAGE (**public**) |
| **Handoff bundle** | Everything too large or too sensitive for git: datasets, `data/` (LSTM `.npz` files, keypoint CSVs, raw frames), footage (`Testing/`, `yolo_testing/`), training runs and weights, eval/label images, zips, benchmark outputs | A folder named `SAGE_handoff` on the team SSD (made from `D:\FYP\PROJECT FILES\handoff` on Hussain's laptop) |

The bundle's `main\` folder mirrors the repo layout. It also contains full copies of `src/`, `tests/` and `docs/`, so it works without git, but **git is the source of truth for code and labels**.

## Restore a working copy

1. Clone the repo and check out the branch you need (`main`, or `pilot/label-cleanup` for the latest phase-3 work):
   ```powershell
   git clone https://github.com/Fatimaliaquat-29/FYP_SAGE.git "D:\SAGE"
   ```
2. Overlay the bundle onto the clone **without overwriting** anything git gave you:
   ```powershell
   robocopy "<SSD>\SAGE_handoff\main" "D:\SAGE" /E /XC /XN /XO /R:1 /W:1
   ```
3. Create a fresh Python environment from `requirements_freeze_hussain.txt` (in the bundle root). Those versions come from Hussain's CUDA laptop. On a CPU-only machine, install the CPU build of torch instead.
4. Fix the absolute paths listed in the bundle's `paths_to_fix.txt` (old `D:\FYP\...`, `C:\Users\...` and `\fatima\` paths in yaml, json, py and md files).

Full instructions: `HANDOFF_README.md` in the bundle root.

## Not in the repo or the bundle

- Python virtual environments (`.venv`, `.venv2`): recreate them (step 3).
- `benchmarks/overnight_yolo26/dataset_view/`: broken NTFS junctions to a folder that no longer exists.
- `datasets/sage_merged_v7_A2/`: the phase-3 hardlink copy. Rebuild it with `benchmarks/phase3_a2/a3_build_copy.py`. That script has absolute paths and is untested on other machines.
- `shared/generate_bbox_dataset.py` and `shared/handlabels.py`: zero-byte stubs. The real scripts are `src/detection/generate_bbox_dataset.py` and `src/detection/handlabels.py`.
- Presentation material: kept separately, not part of this handoff.

## Privacy

The footage and frames show identifiable people. Keep the bundle on team machines and the team SSD only. **The repo is public:** never commit images, video, datasets or weights (`.gitignore` blocks most of them, so check `git status` before every commit). Images already committed stay in git history even if they are deleted later.
