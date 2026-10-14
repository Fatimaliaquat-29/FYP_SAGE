Plain-language reading (written by Claude after the run; numbers quoted from the tables above; the AI verdicts are unverified).

**Where the problems are.** Almost all the evidence points at one place: the **MediaPipe-derived person boxes in the two dim,
fixed-camera clips `Sitting_Dim_HM` and `Standing_Walking_Dim_HM`**.
- Detector flags: Sitting_Dim_HM 19.3% SUSPECTED_MISSING / 48.8% SUSPECTED_PHANTOM (n=861); Standing_Walking_Dim_HM 9.4% / 20.7% (n=748).
  Most bright own-footage clips show 0 flags of either kind.
- AI review: 44/51 sampled Sitting_Dim_HM frames and 14/34 Standing_Walking_Dim_HM frames read as BAD_BOX. **All 58 BAD_BOX
  readings are on MediaPipe-derived labels; none of the 15 sampled hand-drawn frames got one.**
- What it looks like: the person box is not missing, it is **in the wrong place**. It is a low, wide box on the bedding/pillow
  (or a box 2–3× too wide around the desk), while the person stands or sits above it, unboxed. So in those frames the real
  person is effectively unlabelled, and a patch of bedding is labelled "person".
- Exploratory count (region defined after looking, so it is a pointer, not a test): 258/650 MediaPipe-labelled Sitting_Dim_HM
  frames and 85/575 MediaPipe-labelled Standing_Walking_Dim_HM frames have a person box in that bedding region. **0 of the 384
  hand-drawn round6_patch frames from the same two clips do.** Note that the `_r1` copies double these frames in training.

**Dark vs lying vs everywhere.** The flags are concentrated, not spread evenly:
- MediaPipe-derived × dark: 19.1% SUSPECTED_MISSING (n=1,227) vs 0.2% for MediaPipe-derived × bright (n=1,261).
- In the 40 uniformly random sampled frames, the AI marked 6/40 BAD_BOX, all from the two Dim_HM clips.

Whether *lying* is a separate problem cannot be told from this data. The "wider than tall" lying proxy is flagged far more
often (15.0% vs 1.6% SUSPECTED_MISSING), but the misplaced bedding boxes are themselves wide, so the proxy is contaminated by
the same defect.

The lying/fall clips with hand-drawn labels (Bedroom_Falll, TV_Lounge_Fallll, Behind_Chair_HM, Blanket_Cover_HM) have high
PHANTOM rates (54–70% per clip). Those boxes were drawn by a person, so this mostly measures the detector failing on hard
footage, not label errors. They do raise two convention questions for a human:
- 3/3 sampled TV_Lounge_Fallll frames: the AI could not see a person inside the box even with brightening.
- 3/5 sampled Behind_Chair_HM frames: the box sits on a green chair with no visible person (fully occluded person, or mislabel?).

The Slow_fall SUSPECTED_MISSING flags that were sampled (4) are the detector firing on the person's reflection in a glass
panel; the labels looked fine. COCO was not checked (external, human-drawn). Empty-room frames: 0 detector flags in 539.

**Other findings.**
- No leakage: 0 filename or md5 overlap with eval/heldout_objects or handlabels/round6_heldout, and 0 val images md5-identical
  to a train image.
- Class order is identical in sage_classes.py and data.yaml.
- The `old` and `normal` clips appear in train twice under different session names (Hussain_Testing_7_23_26_* and
  Sanawar_Testing_7_22_26_*: 307 + 192 byte-identical frames). With the `_r1` copies, each of those frames is in train 4 times.

**How confident.**
- Fairly confident: the Dim_HM misplaced-box pattern is real. Three independent signals agree: detector disagreement, the AI's
  visual reading, and the position count. They separate cleanly by provenance (MediaPipe vs hand-drawn, same clips).
- Not established: how many frames are affected exactly. The 258 / 85 counts are a post-hoc region envelope, and the AI
  reading is at contact-sheet resolution on 120 of 5,091 checked images and is unverified.
- Weak: anything about lying-specific errors, or about the hand-drawn fall clips. The detector is unreliable exactly there.

**A connection to check, not a conclusion.** The overnight run found B (YOLO26n trained on this data) placing person boxes on
the pillow/bedding on Laying_Dim_HM. A training set that labels bedding as "person" in a dim bedroom is one plausible
cause. This audit does not test that.
