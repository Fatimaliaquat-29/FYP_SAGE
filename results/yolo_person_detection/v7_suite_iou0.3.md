# v5 / v6 / v7 suite -- combined person+object, IoU 0.3

## eval/heldout_objects (general)

200 frames, 640 hand-drawn boxes

| class | n | v5 P | v5 R | v6 P | v6 R | v7 P | v7 R |
|---|---|---|------|------|---|
| person | 93 | 0.91 | 0.62 | 0.95 | 0.66 | 0.98 | 0.62 |
| chair | 90 | 0.67 | 0.20 | 0.45 | 0.20 | 0.56 | 0.20 |
| couch | 276 | 0.83 | 0.66 | 0.98 | 0.70 | 0.92 | 0.68 |
| bed | 86 | 0.91 | 0.72 | 0.94 | 0.17 | 0.81 | 0.40 |
| dining table | 94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.89 | 0.09 |
| tv | 1 | 0.00 | 0.00 | nan | 0.00 | 0.00 | 0.00 |

## round6_heldout (Laying_Dim_HM + Behind_Bed_HM, held back)

298 frames, 967 hand-drawn boxes

| class | n | v5 P | v5 R | v6 P | v6 R | v7 P | v7 R |
|---|---|---|------|------|---|
| person | 226 | 0.96 | 0.21 | 0.96 | 0.22 | 1.00 | 0.22 |
| chair | 443 | 1.00 | 0.31 | 0.93 | 0.11 | 1.00 | 0.74 |
| bed | 298 | nan | 0.00 | 1.00 | 0.01 | 1.00 | 0.49 |

