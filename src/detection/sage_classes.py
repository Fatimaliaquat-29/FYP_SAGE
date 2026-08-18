"""Canonical class list for SAGE object detection.

Shared by the dataset builders, the merge step and the trainer so that a single
ordering is used everywhere. Index order is part of the trained model's
contract -- changing it invalidates every previously trained checkpoint.

`person` is deliberately index 0 so that the person-only labels produced by
generate_bbox_dataset.py remain valid under this list with no remapping.

Classes were chosen for what SAGE actually needs (people, the furniture they
fall onto//near, and COCO's closest stand-ins for medicine containers) rather
than keeping all 80 COCO classes.
"""

SAGE_CLASSES = [
    "person",        # 0  - the fall-detection subject
    "bottle",        # 1  - medicine-container proxy (see caveat below)
    "cup",           # 2  - medicine-container proxy
    "wine glass",    # 3  - medicine-container proxy
    "bowl",          # 4  - medicine-container proxy
    "chair",         # 5  - fall context
    "couch",         # 6  - fall context
    "bed",           # 7  - fall context
    "dining table",  # 8  - fall context
    "toilet",        # 9  - fall context (bathroom falls are high-risk)
    "tv",            # 10 - room context
    "sink",          # 11 - room context
    "refrigerator",  # 12 - room context (kitchen/medication storage)
]

# NOTE: bottle/cup/wine glass/bowl are COCO stand-ins, NOT medicine containers.
# COCO's "bottle" is water/wine/soda bottles. Real pill-bottle detection needs a
# custom-labeled dataset and cannot be auto-generated (MediaPipe only tracks
# human bodies). See docs/YOLO_Phase_Summary.md section 6.

CLASS_TO_INDEX = {name: idx for idx, name in enumerate(SAGE_CLASSES)}

assert SAGE_CLASSES[0] == "person", "person must stay at index 0 (see module docstring)"
assert len(set(SAGE_CLASSES)) == len(SAGE_CLASSES), "duplicate class name in SAGE_CLASSES"
