"""Per-clip frame rotation, verified by eye. Shared by every script that reads footage.

Why this exists
---------------
cv2.VideoCapture ignores a video's rotation metadata and returns the raw stored
pixels. Most players (VLC, phone galleries, WhatsApp) apply that metadata, so a
portrait clip looks perfectly normal everywhere EXCEPT here. Left unhandled, the
detector is shown a sideways room and person detection silently collapses to
~0% on footage that is completely fine.

This bit us for real: `Bedroom_Fall.mov` scored 0/20 on lying-person detection
and was written up as evidence that the model is blind to fallen people. The
frames were simply rotated 90 degrees. Worse, posture is classified from box
aspect ratio (w/h > 1 = horizontal), so in a rotated frame a STANDING person
is wide and gets counted as lying -- the labels themselves become wrong.

NOT metadata-driven
-------------------
`CAP_PROP_ORIENTATION_META` was tried and rejected. All four originals below
report meta=90 but need THREE different corrections: Bedroom_Fall and the
TV_Lounge_2 clips need opposite directions despite identical metadata, and two
clips reporting meta=180 turned out to be already upright. The likely cause is
each clip being filmed with the phone held differently, which a single
per-file metadata field cannot capture.

So there is no reliable automatic rule. Every entry here was confirmed by
looking at a frame. Metadata is used ONLY to flag a clip as suspicious.

Adding a clip
-------------
1. Save a frame: `cv2.imwrite('check.jpg', frame)`
2. Look at it. Ceiling at the top? Then it is upright -- add `None`.
3. Otherwise pick the rotation that puts the ceiling at the top and add it.

Do NOT guess from metadata. An unverified portrait clip is reported by
`needs_verification()` so callers can exclude it rather than measure it wrong.
"""

from pathlib import Path
from typing import Optional

import cv2

# Verified by eye, frame by frame. `None` means "checked, no rotation needed".
VERIFIED_ROTATIONS = {
    # --- originals, verified by the team (Aug 2026) ---
    "Bedroom_Fall.mov": cv2.ROTATE_90_CLOCKWISE,
    "TV_Lounge_2_Fall.mov": cv2.ROTATE_90_COUNTERCLOCKWISE,
    "TV_Lounge_2_Sit.mov": cv2.ROTATE_90_CLOCKWISE,
    "TV_Lounge_2_Walk.mov": cv2.ROTATE_90_CLOCKWISE,
    # --- re-shoots, verified here (Aug 2026) ---
    # All four TV_Lounge_2 re-shoots are stored portrait with the ceiling,
    # chandelier and fan against the RIGHT edge, so the right edge is "up".
    # NOTE they do NOT match their own originals: TV_Lounge_2_Sit/Walk need CW
    # while Sit2/Walk2 need CCW. Same room, same scene, opposite corrections --
    # which is precisely why this table is per-clip and eye-verified.
    "TV_Lounge_2_Empty2.mov": cv2.ROTATE_90_COUNTERCLOCKWISE,
    "TV_Lounge_2_Fall2.mov": cv2.ROTATE_90_COUNTERCLOCKWISE,
    "TV_Lounge_2_Sit2.mov": cv2.ROTATE_90_COUNTERCLOCKWISE,
    "TV_Lounge_2_Walk2.mov": cv2.ROTATE_90_COUNTERCLOCKWISE,
    # Landscape, ceiling already at the top -- confirmed upright.
    "TV_Lounge_1_Empty2.mov": None,
    "TV_Lounge_1_Fall2.mov": None,
    "TV_Lounge_1_Sit2.mov": None,
    "TV_Lounge_1_Walk2.mov": None,
    # Flagged by metadata but confirmed upright by eye.
    "Bedroom_Empty.mov": None,
    "Bedroom_Sit.mov": None,
    "Bedroom_Walk.mov": None,
    "people.mov": None,
    "TV_Lounge_2_Empty.mov": None,
    "empty_ground_mahaRoom.MOV": None,
    "people_ground_mahaRoom.MOV": None,
    # --- round 5: dark / low-contrast / occluded falls (Aug 2026, TRAINING) ---
    # Recorded to fill the gap reserved_heldout_posture_v5.md identifies: a person
    # lying ON furniture, in dark clothing, in a dim room, partly occluded.
    #
    # The bedroom pair needs 90 CCW -- the OPPOSITE of the Reserved
    # `Bedroom_Fall.mov`, which needs 90 CW despite both reporting meta=90 and
    # both being stored 1080x1920. That is why these carry distinct filenames:
    # this table is keyed on the name alone, so a reused name would have applied
    # the wrong correction silently and rotated every frame 180 degrees out.
    "Bedroom_Falll.mov": cv2.ROTATE_90_COUNTERCLOCKWISE,
    "Bedroom_Emptyy.mov": cv2.ROTATE_90_COUNTERCLOCKWISE,
    # Landscape, ceiling fan already at the top -- upright despite meta=180.
    "TV_Lounge_Fallll.mov": None,
    "TV_Lounge_Emptyy.mov": None,
}


def get_rotation(clip_path: Path) -> Optional[int]:
    """cv2.rotate() code for this clip, or None for no rotation."""
    return VERIFIED_ROTATIONS.get(Path(clip_path).name)


def needs_verification(clip_path: Path, capture=None) -> bool:
    """True if this clip looks rotated but nobody has verified which way.

    Callers should EXCLUDE these rather than measure them: a wrong orientation
    does not produce an error, it produces a plausible-looking wrong number.
    """
    path = Path(clip_path)
    if path.name in VERIFIED_ROTATIONS:
        return False

    opened_here = capture is None
    if opened_here:
        capture = cv2.VideoCapture(str(path))
    try:
        meta = capture.get(cv2.CAP_PROP_ORIENTATION_META)
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    finally:
        if opened_here:
            capture.release()

    # Portrait storage OR non-zero orientation metadata: either is enough to
    # doubt it. Landscape with meta=0 is the normal, trustworthy case.
    return bool(meta) or (height > width)


def apply(frame, rotation: Optional[int]):
    """Rotate a frame if a rotation is set."""
    return frame if rotation is None else cv2.rotate(frame, rotation)


def describe(rotation: Optional[int]) -> str:
    return {
        None: "none",
        cv2.ROTATE_90_CLOCKWISE: "90 CW",
        cv2.ROTATE_90_COUNTERCLOCKWISE: "90 CCW",
        cv2.ROTATE_180: "180",
    }.get(rotation, str(rotation))
