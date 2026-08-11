"""Minimal local bounding-box labeller. Drag a box, press SPACE, next image.

Why a local tool rather than Roboflow/CVAT
------------------------------------------
These frames contain identifiable people. `.gitignore` keeps this footage off
GitHub for exactly that reason, and uploading it to a cloud annotation service
would undo that decision silently. This runs entirely on your machine and needs
nothing beyond the opencv already installed.

Writes YOLO format: `<class> <x_center> <y_center> <width> <height>`, all
normalised 0-1 against the ORIGINAL image size (the display is downscaled to
fit the screen; coordinates are converted back).

Resumable: images that already have a .txt are skipped, so you can stop and
restart. Use --redo to relabel them anyway.

Usage
-----
    # label the person in every people_* frame
    python src/detection/label_frames.py --pattern "people*" --class person

    # furniture pass over the empty rooms
    python src/detection/label_frames.py --pattern "beds*" --class chair

Controls
--------
    drag           draw a box
    SPACE / ENTER / n   save boxes for this frame, go to next
    e              save an EMPTY label (nothing of this class in frame)
    u              undo last box
    c              clear all boxes on this frame
    b              go back one image (does not unsave)
    s              skip without saving (frame excluded from scoring)
    1-9            switch active class (see the on-screen legend)
    q / ESC        quit (progress is already saved per-frame)

An EMPTY label is a real statement ("nothing here"), which is why `e` exists
and is not the same as skipping. score_heldout_objects.py excludes images with
no .txt as "not yet labelled", so skipping silently drops the frame from the
measurement instead of counting it.
"""

import argparse
import sys
from pathlib import Path

import cv2

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.sage_classes import CLASS_TO_INDEX, SAGE_CLASSES

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
MAX_DISPLAY = (1600, 900)   # window is capped to this; 4K frames are downscaled

COLORS = [(0, 0, 255), (0, 200, 255), (0, 255, 0), (255, 200, 0), (255, 0, 200)]


class Labeller:
    def __init__(self, class_indices):
        self.class_indices = class_indices
        self.active = 0
        self.boxes = []            # (class_idx, x1, y1, x2, y2) in DISPLAY pixels
        self.drag_start = None
        self.cursor = None

    def on_mouse(self, event, x, y, flags, _param):
        self.cursor = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
        elif event == cv2.EVENT_LBUTTONUP and self.drag_start:
            x0, y0 = self.drag_start
            self.drag_start = None
            if abs(x - x0) > 4 and abs(y - y0) > 4:   # ignore stray clicks
                self.boxes.append((self.class_indices[self.active],
                                   min(x0, x), min(y0, y), max(x0, x), max(y0, y)))

    def draw(self, base, name, index, total, saved):
        canvas = base.copy()
        for cls, x1, y1, x2, y2 in self.boxes:
            color = COLORS[self.class_indices.index(cls) % len(COLORS)]
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
            cv2.putText(canvas, SAGE_CLASSES[cls], (x1, max(18, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        if self.drag_start and self.cursor:
            cv2.rectangle(canvas, self.drag_start, self.cursor, (200, 200, 200), 1)

        active_name = SAGE_CLASSES[self.class_indices[self.active]]
        bar = [
            f"[{index + 1}/{total}] {name}",
            f"class: {active_name}   boxes: {len(self.boxes)}   labelled so far: {saved}",
            "drag=box  SPACE/n=save+next  e=empty(no person)  u=undo  c=clear  b=back  s=skip  q=quit",
        ]
        y = 22
        for line in bar:
            cv2.putText(canvas, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 4)
            cv2.putText(canvas, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
            y += 22
        return canvas


def to_yolo(boxes, disp_w, disp_h):
    """Display-pixel boxes -> normalised YOLO lines."""
    lines = []
    for cls, x1, y1, x2, y2 in boxes:
        cx = ((x1 + x2) / 2) / disp_w
        cy = ((y1 + y2) / 2) / disp_h
        w = abs(x2 - x1) / disp_w
        h = abs(y2 - y1) / disp_h
        lines.append(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return lines


def main():
    parser = argparse.ArgumentParser(description="Minimal local YOLO bounding-box labeller")
    parser.add_argument("--eval_dir", type=str, default=str(REPO_ROOT / "eval" / "heldout_objects"))
    parser.add_argument("--pattern", type=str, default="*",
                        help="Filename glob to label, e.g. 'people*' (default: all)")
    parser.add_argument("--class", dest="classes", type=str, default="person",
                        help="Comma-separated class names available while labelling. "
                             "The first is active on start; switch with number keys.")
    parser.add_argument("--redo", action="store_true",
                        help="Also revisit images that already have a .txt")
    args = parser.parse_args()

    eval_dir = Path(args.eval_dir)
    images_dir, labels_dir = eval_dir / "images", eval_dir / "labels"
    if not images_dir.is_dir():
        raise SystemExit(f"{images_dir} not found -- run sample_heldout_frames.py first.")
    labels_dir.mkdir(parents=True, exist_ok=True)

    class_indices = []
    for raw in args.classes.split(","):
        name = raw.strip().lower()
        if name not in CLASS_TO_INDEX:
            raise SystemExit(f"Unknown class {name!r}. Valid: {', '.join(SAGE_CLASSES)}")
        class_indices.append(CLASS_TO_INDEX[name])

    images = sorted(p for p in images_dir.glob(args.pattern)
                    if p.suffix.lower() in IMAGE_EXTENSIONS)
    if not args.redo:
        images = [p for p in images if not (labels_dir / f"{p.stem}.txt").exists()]
    if not images:
        print("Nothing to label (all matching images already have a .txt -- use --redo to revisit).")
        return

    print(f"{len(images)} image(s) to label from {images_dir}")
    print(f"classes: {', '.join(SAGE_CLASSES[i] for i in class_indices)}")
    print("drag=box  SPACE/n=save+next  e=empty(no person)  u=undo  c=clear  b=back  s=skip  q=quit\n")

    labeller = Labeller(class_indices)
    window = "label"
    cv2.namedWindow(window)
    cv2.setMouseCallback(window, labeller.on_mouse)

    index = 0
    saved = 0
    while 0 <= index < len(images):
        path = images[index]
        image = cv2.imread(str(path))
        if image is None:
            print(f"  skip unreadable {path.name}")
            index += 1
            continue

        h, w = image.shape[:2]
        scale = min(MAX_DISPLAY[0] / w, MAX_DISPLAY[1] / h, 1.0)
        display = cv2.resize(image, (int(w * scale), int(h * scale))) if scale < 1.0 else image.copy()
        dh, dw = display.shape[:2]
        labeller.boxes = []

        while True:
            cv2.imshow(window, labeller.draw(display, path.name, index, len(images), saved))
            key = cv2.waitKey(20) & 0xFF

            # 'n' is accepted here too. It reads as "next" to most people, and
            # binding it to skip-without-saving silently discarded 18 frames of
            # work the first time this tool was used. Advancing keys now SAVE
            # whenever boxes exist; skipping requires the explicit 's'.
            if key in (ord(' '), 13, ord('n')):            # save + next
                if not labeller.boxes:
                    print(f"  {path.name}: no boxes drawn -- press 'e' if the person is not "
                          "in this frame, or 's' to skip it entirely")
                    continue
                (labels_dir / f"{path.stem}.txt").write_text(
                    "\n".join(to_yolo(labeller.boxes, dw, dh)) + "\n", encoding="utf-8")
                saved += 1
                print(f"  {path.name}: {len(labeller.boxes)} box(es)")
                index += 1
                break
            if key == ord('e'):                            # explicit empty
                (labels_dir / f"{path.stem}.txt").write_text("", encoding="utf-8")
                saved += 1
                print(f"  {path.name}: EMPTY (nothing of this class)")
                index += 1
                break
            if key == ord('u') and labeller.boxes:
                labeller.boxes.pop()
            elif key == ord('c'):
                labeller.boxes = []
            elif key == ord('s'):
                print(f"  {path.name}: SKIPPED, no .txt written -- this frame is excluded "
                      "from scoring entirely")
                index += 1
                break
            elif key == ord('b'):
                index = max(0, index - 1)
                break
            elif key in (ord('q'), 27):
                cv2.destroyAllWindows()
                print(f"\nStopped. {saved} label file(s) written to {labels_dir}")
                return
            elif ord('1') <= key <= ord('9'):
                choice = key - ord('1')
                if choice < len(class_indices):
                    labeller.active = choice

    cv2.destroyAllWindows()
    remaining = sum(1 for p in sorted(images_dir.glob(args.pattern))
                    if p.suffix.lower() in IMAGE_EXTENSIONS
                    and not (labels_dir / f"{p.stem}.txt").exists())
    print(f"\nDone. {saved} label file(s) written to {labels_dir}")
    print(f"{remaining} matching image(s) still unlabelled.")
    if remaining == 0:
        print("\nNext:")
        print("  python src/detection/score_heldout_objects.py --classes person \\")
        print("         --model models/yolov8n_sage_merged_v3.pt")


if __name__ == "__main__":
    main()
