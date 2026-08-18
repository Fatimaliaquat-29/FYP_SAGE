# S.A.G.E. — Camera Placement Guidance (person/object detection)

Written after diagnosing why person detection was weak (20-51%) on two of the three
Reserved/ rooms (`TV_Lounge_1`, `TV_Lounge_2`) even though the same YOLO models scored
95%+ in `Bedroom`. Pulled actual frames from each clip to compare — the difference was
the shot, not the model. See `results/yolo_person_detection/reserved_people_v3_conf25.md`
for the numbers this is based on.

This is a companion to `recording_round2.md` §0 ("fix the framing first"), which covers
the *pose/skeleton* framing requirement (MediaPipe needs head-to-feet visible). This
document is about *camera placement* specifically for object detection — a related but
separate failure mode, since YOLO looks at raw pixels, not landmarks.

---

## What went wrong, concretely

**`TV_Lounge_2` (20-51% detection): camera obstructed and too far back.**
The phone was propped low on a shelf/table, with the edge of that surface filling the
bottom-right of every frame. The person ends up small, distant, and partially blocked
by furniture in the foreground. Pulling actual frames confirmed this holds throughout
the clip, not just at one bad moment.

**`TV_Lounge_1_Fall` (27-31% detection): a deeper problem, not fixable by camera angle
alone.** Frames here are well-lit and full-body — but a person lying/collapsed onto
that room's light, heavily-textured couch gets *zero* person detections, even at
confidence ≥0.01. The whole region reads as "couch" instead. This is the same
furniture-absorption pattern found for people lying on beds (which a lower confidence
threshold fixed), except here there's no signal at any threshold to recover — the model
has essentially no learned representation for this specific look. **No camera placement
fixes this one** — it needs more labeled training examples of people lying on
light/patterned upholstery. Noted here so it isn't mistaken for a framing issue next
time someone reads a low TV_Lounge_1 number.

---

## Rules for future recording (object/person detection footage)

1. **Prop the camera, don't hold it** (already in `TESTING_GUIDE.md` — handheld footage
   drifts and breaks frame-labelling assumptions too).
2. **Nothing in the foreground.** Check the live preview before recording — if any
   object (shelf edge, table, plant) crosses the bottom or side of frame closer to the
   camera than the subject, move the camera. It doesn't just look bad, it directly
   costs detection accuracy at that distance.
3. **Distance: full body, not filling the frame, not a speck.** Two failure directions,
   both seen this round:
   - *Too close* (`TV_Lounge_1`, some frames): subject fills the frame edge-to-edge,
     head cropped out. Back away or zoom out.
   - *Too far* (`TV_Lounge_2`): subject is a small, low-detail blob. Move the camera
     closer or reframe so the person occupies a meaningfully large fraction of frame
     even at their farthest point of movement in the room.
   - `Bedroom`, which scored 95-99%, is the reference: full body, moderate distance,
     camera roughly eye-height, nothing between camera and subject.
4. **Walk the intended path before recording and watch the live preview the whole
   time**, not just at the start. A shot that looks fine at frame 1 can still crop or
   obstruct the subject once they move (this is exactly what happened on part of
   `TV_Lounge_1`).
5. **If the subject will lie down on a couch/sofa as part of the clip**, note in the
   filename or a comment which room/couch it is — this is the scenario most likely to
   hit the furniture-absorption gap above, and it's useful to know which specific couch
   appearances have been tested versus not, going forward.

## Quick check before recording a batch

Run the same live preview workflow `recording_round2.md` already recommends for pose:

```
python realtime_fall_detection.py --input 1 --object-model models/yolov8n_sage_merged_v3.pt
```

This now also draws YOLO's person/furniture boxes live (as of the object-detection +
pose integration), so you can directly see whether the person box is firing reliably
in the intended spot *before* committing to a full recording session, not after.
