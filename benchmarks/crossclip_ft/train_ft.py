"""Cross-clip fine-tune: v7 + the corrected Behind_Bed_HM frames, tested on the unseen Laying_Dim_HM clip.

Run 1 of the cross-clip design (PROVISIONAL: the corrected round6_heldout_v2 labels are not yet
verified). The 153 Laying_Dim_HM frames are never in train or val, so scoring on them is fair.

Starting weights: models/yolov8n_sage_merged_v7.pt (fine-tune, not a fresh 30-epoch retrain).
Settings: v7's recorded train_args, except:
  data     -> data_ft.yaml (v7 train list + 145 Behind_Bed_HM frames; v7 val list)
  epochs   -> EPOCHS (short fine-tune; v7 used 30)
  warmup_epochs 3 -> 1, close_mosaic 10 -> 2 (scaled down for the short schedule)
  device   -> cpu, workers -> 4 (no GPU on this machine)
  project/name -> benchmarks/crossclip_ft/runs/<name>
The train list starts with the round6_heldout_v2 frames so Ultralytics writes its label cache
next to those labels, not over datasets/sage_merged_v7/labels/train.cache.

Usage:
  python train_ft.py lists            write train_ft.txt / val_ft.txt / data_ft.yaml
  python train_ft.py time             1 epoch on 5% of the data, to estimate epoch time
  python train_ft.py train [EPOCHS]   the fine-tune (default 5 epochs)
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
V7 = REPO / "models" / "yolov8n_sage_merged_v7.pt"
V7_DATA = REPO / "datasets" / "sage_merged_v7"
NEW = REPO / "handlabels" / "round6_heldout_v2"
TEST_CLIP = "Laying_Dim_HM"   # never trained on
TRAIN_CLIP = "Behind_Bed_HM"  # added to training
NAMES = ["person", "bottle", "cup", "wine glass", "bowl", "chair", "couch", "bed",
         "dining table", "toilet", "tv", "sink", "refrigerator"]


def write_lists():
    new = sorted((NEW / "images").glob(f"{TRAIN_CLIP}_*.jpg"))
    assert len(new) == 145, len(new)
    assert not any(TEST_CLIP in p.name for p in new)
    v7_train = sorted((V7_DATA / "images" / "train").glob("*.jpg"))
    v7_val = sorted((V7_DATA / "images" / "val").glob("*.jpg"))
    # leakage guard: the held-out clips must not already be inside v7's data
    for p in v7_train + v7_val:
        assert TEST_CLIP not in p.name and TRAIN_CLIP not in p.name, p
    (HERE / "train_ft.txt").write_text("\n".join(p.as_posix() for p in new + v7_train) + "\n", encoding="utf-8")
    (HERE / "val_ft.txt").write_text("\n".join(p.as_posix() for p in v7_val) + "\n", encoding="utf-8")
    yaml = [f"path: {HERE.as_posix()}", "train: train_ft.txt", "val: val_ft.txt", "names:"]
    yaml += [f"  {i}: {n}" for i, n in enumerate(NAMES)]
    (HERE / "data_ft.yaml").write_text("\n".join(yaml) + "\n", encoding="utf-8")
    print(f"train: {len(new)} new + {len(v7_train)} v7 = {len(new) + len(v7_train)}; val: {len(v7_val)}")


def args_for(name, epochs, **extra):
    import torch
    rec = torch.load(V7, weights_only=False, map_location="cpu")["train_args"]
    args = dict(rec)
    args.pop("model", None)
    args.pop("resume", None)
    args.update(data=str(HERE / "data_ft.yaml"), epochs=epochs, warmup_epochs=1.0, close_mosaic=2,
                device="cpu", workers=4, project=str(HERE / "runs"), name=name, exist_ok=False,
                amp=False, plots=True)
    args.update(extra)
    return args


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "lists":
        write_lists(); return
    from ultralytics import YOLO
    if cmd == "time":
        t = time.time()
        YOLO(str(V7)).train(**args_for("timing", 1, fraction=0.05, val=False, plots=False))
        print(f"TIMING: 1 epoch on 5% took {time.time() - t:.0f} s", flush=True)
        return
    if cmd == "train":
        epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        args = args_for("ft_behindbed", epochs)
        (HERE / "train_ft_effective_args.json").write_text(json.dumps(args, indent=2, default=str), encoding="utf-8")
        YOLO(str(V7)).train(**args)
        return
    print(__doc__)


if __name__ == "__main__":
    main()
