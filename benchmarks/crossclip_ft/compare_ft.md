# v7 vs v7 + Behind_Bed_HM fine-tune, on frames neither model trained on

PROVISIONAL: the corrected labels are not yet verified. Fine-tune: v7 weights + 5 epochs on
v7's training data plus the 145 corrected Behind_Bed_HM frames (see train_ft.py).

## IoU 0.5

### Laying_Dim_HM (dark, unseen), corrected labels [PROVISIONAL]

153 frames, 459 labelled boxes (0 unlabelled, excluded)

| class | n | v7 (current) P | v7 (current) R | v7 + Behind_Bed fine-tune P | v7 + Behind_Bed fine-tune R |
|---|---|---|---|---|---|
| person | 153 | 1.00 | 0.01 (2/153, fp 0) | 0.00 | 0.00 (0/153, fp 7) |
| chair | 153 | 1.00 | 0.25 (39/153, fp 0) | 1.00 | 0.98 (150/153, fp 0) |
| bed | 153 | 1.00 | 0.01 (1/153, fp 0) | 1.00 | 0.08 (13/153, fp 0) |

### Laying_Dim_HM (dark, unseen), original labels

153 frames, 459 labelled boxes (0 unlabelled, excluded)

| class | n | v7 (current) P | v7 (current) R | v7 + Behind_Bed fine-tune P | v7 + Behind_Bed fine-tune R |
|---|---|---|---|---|---|
| person | 153 | 1.00 | 0.01 (2/153, fp 0) | 0.00 | 0.00 (0/153, fp 7) |
| chair | 153 | 1.00 | 0.25 (39/153, fp 0) | 1.00 | 0.98 (150/153, fp 0) |
| bed | 153 | 1.00 | 0.01 (1/153, fp 0) | 1.00 | 0.08 (13/153, fp 0) |

### eval/heldout_objects (general, unseen)

200 frames, 640 labelled boxes (0 unlabelled, excluded)

| class | n | v7 (current) P | v7 (current) R | v7 + Behind_Bed fine-tune P | v7 + Behind_Bed fine-tune R |
|---|---|---|---|---|---|
| person | 93 | 0.98 | 0.62 (58/93, fp 1) | 0.97 | 0.65 (60/93, fp 2) |
| chair | 90 | 0.56 | 0.20 (18/90, fp 14) | 0.91 | 0.23 (21/90, fp 2) |
| couch | 276 | 0.82 | 0.61 (168/276, fp 36) | 0.64 | 0.38 (106/276, fp 59) |
| bed | 86 | 0.17 | 0.08 (7/86, fp 35) | 0.40 | 0.27 (23/86, fp 35) |
| dining table | 94 | 0.89 | 0.09 (8/94, fp 1) | 0.48 | 0.11 (10/94, fp 11) |
| tv | 1 | 0.00 | 0.00 (0/1, fp 1) | n/a | 0.00 (0/1, fp 0) |

## IoU 0.3

### Laying_Dim_HM (dark, unseen), corrected labels [PROVISIONAL]

153 frames, 459 labelled boxes (0 unlabelled, excluded)

| class | n | v7 (current) P | v7 (current) R | v7 + Behind_Bed fine-tune P | v7 + Behind_Bed fine-tune R |
|---|---|---|---|---|---|
| person | 153 | 1.00 | 0.01 (2/153, fp 0) | 0.00 | 0.00 (0/153, fp 7) |
| chair | 153 | 1.00 | 0.25 (39/153, fp 0) | 1.00 | 0.98 (150/153, fp 0) |
| bed | 153 | 1.00 | 0.01 (1/153, fp 0) | 1.00 | 0.08 (13/153, fp 0) |

### Laying_Dim_HM (dark, unseen), original labels

153 frames, 459 labelled boxes (0 unlabelled, excluded)

| class | n | v7 (current) P | v7 (current) R | v7 + Behind_Bed fine-tune P | v7 + Behind_Bed fine-tune R |
|---|---|---|---|---|---|
| person | 153 | 1.00 | 0.01 (2/153, fp 0) | 0.00 | 0.00 (0/153, fp 7) |
| chair | 153 | 1.00 | 0.25 (39/153, fp 0) | 1.00 | 0.98 (150/153, fp 0) |
| bed | 153 | 1.00 | 0.01 (1/153, fp 0) | 1.00 | 0.08 (13/153, fp 0) |

### eval/heldout_objects (general, unseen)

200 frames, 640 labelled boxes (0 unlabelled, excluded)

| class | n | v7 (current) P | v7 (current) R | v7 + Behind_Bed fine-tune P | v7 + Behind_Bed fine-tune R |
|---|---|---|---|---|---|
| person | 93 | 0.98 | 0.62 (58/93, fp 1) | 0.97 | 0.65 (60/93, fp 2) |
| chair | 90 | 0.56 | 0.20 (18/90, fp 14) | 0.91 | 0.23 (21/90, fp 2) |
| couch | 276 | 0.92 | 0.68 (187/276, fp 17) | 0.81 | 0.49 (134/276, fp 31) |
| bed | 86 | 0.81 | 0.40 (34/86, fp 8) | 0.59 | 0.40 (34/86, fp 24) |
| dining table | 94 | 0.89 | 0.09 (8/94, fp 1) | 0.48 | 0.11 (10/94, fp 11) |
| tv | 1 | 0.00 | 0.00 (0/1, fp 1) | n/a | 0.00 (0/1, fp 0) |

