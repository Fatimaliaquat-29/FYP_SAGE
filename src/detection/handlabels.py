"""Hand-drawn YOLO labels, loaded and validated as a first-class label source.

Why this exists
---------------
Every person label in the training set has so far come from MediaPipe, via
generate_bbox_dataset.py. That is fine for upright people and it is exactly
wrong for the case this project cares about: MediaPipe covers only ~46% of the
hardest fall frames even in VIDEO mode -- a person lying ON furniture, in dark
clothing, in a dim room, partly occluded.

Round 5 was recorded to BE that hard case and was hand-labelled for precisely
that reason (55bad29). But there was no route from a hand-drawn .txt into a
training set, so those 104 person boxes could not reach a model at all. This
module is that route.

The one rule that matters
-------------------------
Hand labels WIN over MediaPipe on any frame that has both, and they win
regardless of --stride. Falling back to MediaPipe on a frame a human already
judged is what made v5 fail to move the fall column: the auto-labeller emits
nothing on the hardest frames, so those frames were simply absent from
training. A hand label is ground truth; a MediaPipe box is a guess.

Labels are the source of truth, images are not
----------------------------------------------
`handlabels/**/*.jpg` is gitignored (identifiable people, same rule as `eval/`),
so a fresh clone has the .txt files and no frames. The frames are therefore
REGENERATED from the source clips rather than copied, which means this path
works from a clean checkout. When a local .jpg does happen to be present it is
used as a checksum -- see `verify_frame`. That check is the difference between
"the labels line up" and "we assumed the labels line up", and given that a 90
degree rotation error produces plausible-looking boxes on a plausible-looking
image, assuming is not good enough.

Index space
-----------
classes.txt must match SAGE_CLASSES exactly. A YOLO .txt stores an integer, and
that integer means whatever the labelling tool's class list said it meant; a
file drawn against a different ordering would train `couch` boxes as `wine
glass` with a perfectly healthy-looking loss curve. Same failure
build_merged_dataset.py remaps by name to avoid -- but here there is nothing to
remap by, because a bare .txt carries no names. So the only safe move is to
refuse anything whose class list is not identical.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.detection.sage_classes import SAGE_CLASSES

# Mean absolute pixel difference allowed between a regenerated frame and the
# committed .jpg of the same frame. Not zero: the .jpg was JPEG-encoded once, so
# decoding it back never reproduces the source frame exactly. A few units of
# codec noise is normal; anything larger means the frames are not the same
# picture. The failures this is aimed at are not subtle -- a wrong rotation, a
# wrong stride or an off-by-one frame index all land far above this.
FRAME_MATCH_TOLERANCE = 10.0


class HandLabelError(SystemExit):
    """Raised for any condition that would silently mislabel training data."""


class HandLabelSet:
    """One hand-labelled frame set, e.g. `handlabels/round5/`.

    Expects the layout sample_heldout_frames.py writes and a human then fills:

        <root>/classes.txt          one class name per line, == SAGE_CLASSES
        <root>/labels/<stem>.txt    YOLO boxes, <stem> == <clip_stem>_<frame:06d}
        <root>/images/<stem>.jpg    optional; gitignored, used only to verify

    Consumption is tracked so `unconsumed()` can report labels no clip claimed.
    An orphaned label is invisible otherwise: the run succeeds, the dataset
    looks fine, and the hand-drawn work is simply missing from it.
    """

    def __init__(self, root: Path):
        self.root = Path(root)
        self.labels_dir = self.root / "labels"
        self.images_dir = self.root / "images"

        if not self.labels_dir.is_dir():
            raise HandLabelError(f"{self.root}: no labels/ directory -- nothing to merge.")

        self._assert_class_list_matches()

        # classes.txt is commonly saved INTO labels/ by labelling tools
        # (labelImg does this), so it must never be read as a set of boxes.
        self.boxes = {}
        for path in sorted(self.labels_dir.glob("*.txt")):
            if path.name == "classes.txt":
                continue
            self.boxes[path.stem] = self._parse(path)

        if not self.boxes:
            raise HandLabelError(f"{self.labels_dir}: contains no label files.")

        self.consumed = set()

    def _assert_class_list_matches(self):
        classes_file = self.root / "classes.txt"
        if not classes_file.is_file():
            raise HandLabelError(
                f"{classes_file} not found.\n"
                "  A YOLO .txt stores only integers, so without the class list that produced\n"
                "  them there is no way to know what those integers mean. Refusing to guess."
            )
        names = [line.strip().lower() for line in
                 classes_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        if names != [n.lower() for n in SAGE_CLASSES]:
            raise HandLabelError(
                f"{classes_file} does not match SAGE_CLASSES.\n"
                f"  file: {names}\n"
                f"  sage: {SAGE_CLASSES}\n"
                "  These labels were drawn against a different index space, so merging them\n"
                "  would train each box as the wrong class -- with a healthy-looking loss\n"
                "  curve, because nothing about a wrong-but-valid index is detectable later.\n"
                "  Re-export the labels against src/detection/sage_classes.py."
            )

    def _parse(self, path: Path):
        """Validate one label file and return its lines. Aborts rather than skips.

        Skipping a malformed line would drop a hand-drawn box -- the one kind of
        label in this project that cannot be regenerated by re-running anything.
        """
        lines = []
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            text = raw.strip()
            if not text:
                continue
            parts = text.split()
            where = f"{path.name}:{lineno}"
            if len(parts) != 5:
                raise HandLabelError(
                    f"{where}: expected '<class> <xc> <yc> <w> <h>', got {len(parts)} fields: {text!r}")
            try:
                class_idx = int(float(parts[0]))
                xc, yc, w, h = (float(v) for v in parts[1:])
            except ValueError:
                raise HandLabelError(f"{where}: non-numeric field in {text!r}")

            if not 0 <= class_idx < len(SAGE_CLASSES):
                raise HandLabelError(
                    f"{where}: class index {class_idx} is outside SAGE_CLASSES "
                    f"(0..{len(SAGE_CLASSES) - 1}).")
            if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0):
                raise HandLabelError(
                    f"{where}: centre ({xc}, {yc}) is outside the frame. YOLO coordinates are "
                    "normalised 0-1; pixel coordinates here would be silently unlearnable.")
            if not (0.0 < w <= 1.0 and 0.0 < h <= 1.0):
                raise HandLabelError(f"{where}: width/height ({w}, {h}) must be in (0, 1].")

            lines.append(f"{class_idx} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
        return lines

    def take(self, stem: str):
        """Return this frame's label lines and mark it consumed, or None.

        None means "no human labelled this frame", which is the caller's cue to
        fall back to MediaPipe. An empty LIST is different and meaningful: a
        frame a human looked at and found nothing in, i.e. a background
        negative. Do not collapse the two.
        """
        if stem not in self.boxes:
            return None
        self.consumed.add(stem)
        return self.boxes[stem]

    def verify_frame(self, stem: str, frame) -> bool:
        """Cross-check a regenerated frame against the committed .jpg, if present.

        Returns True if verified, False if there was no image to check against.
        Raises on mismatch.

        This catches the failure mode that regeneration invites: the boxes are
        drawn on a frame produced by a specific (clip, rotation, frame index)
        triple, and reproducing any of those three wrongly yields a normal-
        looking image with every box in the wrong place. A wrong rotation shows
        up as a transposed shape, a wrong frame index as a large pixel delta.
        """
        image_path = self.images_dir / f"{stem}.jpg"
        if not image_path.is_file():
            return False

        import cv2
        import numpy as np

        reference = cv2.imread(str(image_path))
        if reference is None:
            raise HandLabelError(f"{image_path} exists but could not be decoded.")

        if reference.shape != frame.shape:
            raise HandLabelError(
                f"{stem}: regenerated frame is {frame.shape[1]}x{frame.shape[0]} but the frame "
                f"the boxes were drawn on is {reference.shape[1]}x{reference.shape[0]}.\n"
                "  A transposed shape means the rotation applied here differs from the one\n"
                "  used at labelling time -- check src/detection/footage_rotation.py."
            )

        delta = float(np.mean(np.abs(reference.astype("int16") - frame.astype("int16"))))
        if delta > FRAME_MATCH_TOLERANCE:
            raise HandLabelError(
                f"{stem}: regenerated frame differs from the labelled one "
                f"(mean abs diff {delta:.1f} > {FRAME_MATCH_TOLERANCE}).\n"
                "  Same size but different picture: usually a frame-index or stride mismatch,\n"
                "  or a 180 degree rotation. The boxes would sit on the wrong frame."
            )
        return True

    def unconsumed(self):
        """Stems no clip claimed -- hand-drawn work that did not reach the dataset."""
        return sorted(set(self.boxes) - self.consumed)

    def clip_stems(self):
        """Clip stems these labels refer to, inferred from the frame naming."""
        return sorted({stem.rsplit("_", 1)[0] for stem in self.boxes})

    def __len__(self):
        return len(self.boxes)


class HandLabelUnion:
    """Several label sets addressed as one, so callers stay set-count agnostic.

    Frame stems are guaranteed unique across the member sets (see `load_all`),
    so every lookup resolves to exactly one set and there is no precedence rule
    to get wrong.
    """

    def __init__(self, sets):
        self.sets = list(sets)
        self._owner = {stem: s for s in self.sets for stem in s.boxes}

    def take(self, stem: str):
        owner = self._owner.get(stem)
        return None if owner is None else owner.take(stem)

    def verify_frame(self, stem: str, frame) -> bool:
        owner = self._owner.get(stem)
        return False if owner is None else owner.verify_frame(stem, frame)

    def unconsumed(self):
        return sorted(stem for s in self.sets for stem in s.unconsumed())

    def clip_stems(self):
        return sorted({stem for s in self.sets for stem in s.clip_stems()})

    def __len__(self):
        return len(self._owner)


def load_all(roots):
    """Load several hand-label sets as one union, refusing overlapping stems.

    Two sets claiming the same stem is unresolvable: whichever loaded last would
    win by accident, and the boxes that lost would vanish without a trace.
    """
    sets = [HandLabelSet(Path(root)) for root in roots]
    seen = {}
    for label_set in sets:
        for stem in label_set.boxes:
            if stem in seen:
                raise HandLabelError(
                    f"Frame {stem!r} is labelled in both {seen[stem]} and {label_set.root}.\n"
                    "  Refusing to pick one silently -- rename the frames or drop a set.")
            seen[stem] = label_set.root
    return HandLabelUnion(sets)
