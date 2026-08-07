"""Canonical footage locations, and the guard that keeps reserved data reserved.

Layout
------
Footage lives in TWO trees, on purpose.

    Testing/                <- SHARED recording sessions. Do not restructure.
        Hussain Testing 7-23-26/
        Sanawar Testing 7-22-26/    each: clips + matching _gt.csv sidecars
        Sanawar Testing 7-25-26/
        README.md

    yolo_testing/           <- YOLO-only footage
        Training/           may be used for training
            Empty/              empty rooms -> background negatives
            With people/        (empty; person source is Testing/ above)
        Reserved/           MUST NEVER be trained on
            Empty/              held-out empty room -> false-positive gate
            With people/        held-out room+person -> honest recall test

`Testing/` is shared with the fall-detection track, which reads the same clips
and their ground-truth CSVs. Splitting it would break that work, so YOLO reads
it where it is rather than moving it. `yolo_testing/` holds only footage that
YOLO alone cares about: background negatives and the held-out evaluation set.

A useful side effect: because the session clips never moved, their sorted order
is unchanged, so the index-based train/val split still matches every previously
reported number.

Why the guard exists
--------------------
`Reserved/` sits INSIDE `yolo_testing/`, and the dataset builders discover clips
by rglob-ing the directory they are given. So a single run with a too-shallow
--testing_dir would sweep the reserved footage into training and destroy its
only value -- permanently, since "held out" cannot be restored by moving files
back afterwards. This has already happened once in this project's history.

The older layout defended against that by scattering held-out footage across
sibling directories (Testing_EmptyHeldOut/, Testing_HeldOutEval/), i.e. by
convention plus a README. This module replaces that with an actual refusal:
assert_not_reserved() aborts, so the mistake becomes an error message instead
of a quietly invalid result.

Two further traps this module encodes
-------------------------------------
1. TRAINING_PEOPLE points at `Testing/` itself, and TRAINING_EMPTY at
   `yolo_testing/Training/Empty` -- never at a shared parent of both.
   generate_bbox_dataset.py assigns train/val BY POSITION in the sorted clip
   listing, so widening the path folds extra clips into the same listing,
   shifts every index, and silently changes which clips are held out --
   invalidating every previously reported number.

2. Evaluation scripts (benchmark_footage.py, score_heldout_objects.py) SHOULD
   read Reserved/ -- that is what it is for. Only the training-data producers
   are guarded. The distinction is "does this path feed a training set", not
   "does this path get read".
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FOOTAGE_ROOT = REPO_ROOT / "yolo_testing"

# Person/fall footage lives in Testing/, NOT under yolo_testing/. That tree is
# the shared recording-session archive (Hussain's fall-detection work reads the
# same clips and their _gt.csv sidecars), so it is deliberately left alone --
# see Testing/README.md. Pointing here also preserves the existing train/val
# split exactly, because the clip ordering is unchanged from before the
# yolo_testing/ split was introduced.
SESSION_FOOTAGE = REPO_ROOT / "Testing"
TRAINING_PEOPLE = SESSION_FOOTAGE

TRAINING_ROOT = FOOTAGE_ROOT / "Training"
TRAINING_EMPTY = TRAINING_ROOT / "Empty"
# Empty on purpose: person footage comes from Testing/ (see SESSION_FOOTAGE).
# Kept as the place for any future person footage recorded for YOLO alone. If
# you ever put clips here, note they will NOT be picked up by the default
# --testing_dir, and combining both sources shifts the index-based train/val
# assignment -- see trap 1 above.
TRAINING_PEOPLE_YOLO_ONLY = TRAINING_ROOT / "With people"

RESERVED_ROOT = FOOTAGE_ROOT / "Reserved"
RESERVED_EMPTY = RESERVED_ROOT / "Empty"
RESERVED_PEOPLE = RESERVED_ROOT / "With people"

# Matched case-insensitively against every path component, so a nested
# yolo_testing/Training/With people/Reserved_new_room/ is caught too.
RESERVED_MARKER = "reserved"


def is_reserved(path: Path) -> bool:
    """True if any component of `path` marks it as held-out footage."""
    return any(part.strip().lower() == RESERVED_MARKER for part in Path(path).resolve().parts)


def assert_not_reserved(path: Path, purpose: str) -> None:
    """Abort if `path` would feed reserved footage into training.

    Call this in anything that PRODUCES training data. Do not call it in
    evaluation scripts -- reading Reserved/ is exactly their job.
    """
    if is_reserved(path):
        raise SystemExit(
            f"Refusing to use {path} for {purpose}.\n"
            f"  That path is under '{RESERVED_ROOT.name}/', which is held out of ALL training.\n"
            "  Its entire value is that no model has seen it; one training run ends that\n"
            "  permanently, and moving the files back afterwards does not restore it.\n"
            f"  For training footage use: {TRAINING_PEOPLE}\n"
            f"  For background negatives:  {TRAINING_EMPTY}"
        )


def warn_if_shallow(path: Path) -> None:
    """Warn when `path` is Training/ itself rather than one of its leaves.

    Not fatal -- someone may genuinely want both -- but it changes the clip
    ordering that train/val assignment depends on, so it should never happen
    silently. See trap 1 in the module docstring.
    """
    if Path(path).resolve() == TRAINING_ROOT.resolve():
        print(f"WARNING: {path} contains both Empty/ and 'With people'/.")
        print("         Clip train/val split is assigned BY POSITION in the sorted listing,")
        print("         so including Empty/ here shifts every index and changes which clips")
        print("         are held out -- invalidating comparisons against earlier runs.")
        print(f"         You almost certainly want: {TRAINING_PEOPLE}")
