# Person box fit on our own test footage (PROVISIONAL labels)

Sets: reserved388_partial, round6_heldout (images de-duplicated). Each hand-labelled person box is paired with the model's best-overlapping person box (conf >= 0.4); pairs with IoU < 0.3 count as missed.

- **coverage** = share of the labelled box the model's box covers (below ~90% = the box cuts off part of the person)
- **size ratio** = model box area / labelled box area (above 1 = looser than the label, below 1 = tighter)

| model | labelled people | matched | median IoU | median coverage | matched boxes covering >= 90% | median size ratio | size ratio 10th-90th pct |
|---|---|---|---|---|---|---|---|
| A | 475 | 159 | 0.86 | 93% | 94/159 | 0.99 | 0.80-1.17 |
| B | 475 | 154 | 0.85 | 95% | 103/154 | 1.00 | 0.82-1.20 |
| C | 475 | 165 | 0.85 | 95% | 106/165 | 1.02 | 0.85-1.34 |

Close-up sheets: box_fit_sheet_A.jpg, box_fit_sheet_B.jpg, box_fit_sheet_C.jpg.
