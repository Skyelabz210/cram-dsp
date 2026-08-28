# Scales — units for readings the machine already takes

Run: `python3 analysis/dresden_scales.py`; receipts
`data/dresden/scale_receipts.json`.

**4 exact checks, 0 failures.**

These two instruments attach a unit to numbers that previously had none.
They gate nothing and close nothing (docs/RULES_OF_EXPLORATION.md); a
reading inside its scale is as interesting as one outside it, and both
are simply readings.

## S1 — path-agreement scale

For each page: the minimum pairwise agreement among the three orderings
(brightness / spatial / gradient-flow) over the top 12 nodes, against 15
seeded shuffles that permute node POSITIONS while keeping every node's
brightness, contrast, gradient and chroma exactly. The shuffle isolates
one thing: whether where the bright structures sit relates to the
brightness field's own ordering.

Pages measured: **78**. Observed agreement above every shuffle: **8**.
Observed agreement inside the shuffled range: **70**.

| Scan | Page | Nodes | Observed | Shuffled min | Shuffled median | Shuffled max | Shuffles >= observed |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 312 | 651 | 439 | 606 | 696 | 3 |
| 2 | 2 | 344 | 439 | 454 | 590 | 893 | 15 |
| 3 | 3 | 162 | 696 | 424 | 530 | 757 | 3 |
| 4 | 4 | 427 | 424 | 333 | 590 | 712 | 14 |
| 5 | 5 | 340 | 530 | 393 | 590 | 742 | 10 |
| 6 | 6 | 374 | 606 | 439 | 575 | 636 | 5 |
| 7 | 7 | 364 | 621 | 424 | 590 | 803 | 7 |
| 8 | 8 | 269 | 469 | 106 | 439 | 560 | 7 |
| 9 | 9 | 341 | 469 | 242 | 484 | 818 | 8 |
| 10 | 10 | 384 | 151 | 181 | 439 | 621 | 15 |
| 11 | 11 | 407 | 666 | 454 | 606 | 863 | 5 |
| 12 | 12 | 378 | 484 | 212 | 454 | 636 | 7 |
| 13 | 13 | 398 | 500 | 318 | 545 | 712 | 10 |
| 14 | 14 | 465 | 772 | 242 | 454 | 651 | 0 |
| 15 | 15 | 420 | 227 | 106 | 393 | 515 | 13 |
| 16 | 16 | 417 | 454 | 439 | 560 | 757 | 14 |
| 17 | 17 | 428 | 696 | 333 | 606 | 757 | 4 |
| 18 | 18 | 403 | 181 | 166 | 515 | 681 | 14 |
| 19 | 19 | 381 | 696 | 393 | 606 | 681 | 0 |
| 20 | 20 | 373 | 621 | 378 | 606 | 848 | 5 |
| 21 | 21 | 373 | 696 | 378 | 545 | 727 | 1 |
| 22 | 22 | 365 | 469 | 348 | 575 | 772 | 12 |
| 23 | 23 | 289 | 621 | 393 | 606 | 772 | 7 |
| 24 | 24 | 231 | 606 | 469 | 575 | 712 | 6 |
| 25 | 25 | 385 | 621 | 439 | 590 | 757 | 6 |
| 26 | 26 | 430 | 515 | 454 | 590 | 863 | 10 |
| 27 | 27 | 394 | 636 | 454 | 606 | 742 | 5 |
| 28 | 28 | 305 | 439 | 454 | 606 | 727 | 15 |
| 29 | 28* | 412 | 757 | 439 | 530 | 712 | 0 |
| 30 | 28** | 352 | 484 | 484 | 666 | 772 | 15 |
| 31 | 28*** | 216 | 545 | 409 | 621 | 742 | 9 |
| 32 | 29 | 417 | 742 | 393 | 530 | 727 | 0 |
| 33 | 30 | 354 | 530 | 181 | 515 | 757 | 7 |
| 34 | 31 | 284 | 45 | 181 | 484 | 621 | 15 |
| 35 | 32 | 340 | 166 | 318 | 515 | 666 | 15 |
| 36 | 33 | 409 | 696 | 409 | 590 | 696 | 1 |
| 37 | 34 | 456 | 515 | 333 | 545 | 681 | 10 |
| 38 | 35 | 424 | 636 | 454 | 575 | 742 | 5 |
| 39 | 36 | 318 | 227 | 45 | 454 | 712 | 14 |
| 40 | 37 | 332 | 560 | 378 | 469 | 606 | 4 |
| 41 | 38 | 411 | 500 | 409 | 545 | 666 | 13 |
| 42 | 39 | 393 | 303 | 121 | 409 | 757 | 14 |
| 43 | 40 | 441 | 272 | 242 | 454 | 651 | 14 |
| 44 | 41 | 368 | 606 | 484 | 621 | 727 | 8 |
| 45 | 42 | 377 | 590 | 212 | 500 | 696 | 3 |
| 46 | 43 | 349 | 348 | 484 | 636 | 712 | 15 |
| 47 | 44 | 389 | 484 | 257 | 439 | 621 | 6 |
| 48 | 45 | 375 | 515 | 90 | 545 | 742 | 9 |
| 49 | 46 | 443 | 606 | 409 | 606 | 742 | 8 |
| 50 | 47 | 412 | 318 | 227 | 454 | 621 | 14 |
| 51 | 48 | 363 | 515 | 151 | 484 | 636 | 6 |
| 52 | 49 | 435 | 560 | 333 | 500 | 651 | 4 |
| 53 | 50 | 367 | 333 | 212 | 530 | 621 | 12 |
| 54 | 51 | 437 | 727 | 303 | 545 | 696 | 0 |
| 55 | 52 | 435 | 772 | 409 | 545 | 742 | 0 |
| 56 | 53 | 420 | 272 | 257 | 530 | 696 | 14 |
| 57 | 54 | 450 | 212 | 227 | 424 | 621 | 15 |
| 58 | 55 | 415 | 515 | 333 | 575 | 772 | 9 |
| 59 | 56 | 453 | 560 | 439 | 575 | 712 | 10 |
| 60 | 57 | 467 | 560 | 75 | 484 | 742 | 5 |
| 61 | 58 | 339 | 106 | 212 | 515 | 666 | 15 |
| 62 | 59 | 350 | 848 | 378 | 575 | 696 | 0 |
| 63 | 60 | 416 | 772 | 318 | 590 | 818 | 1 |
| 64 | 60* | 376 | 500 | 181 | 469 | 606 | 6 |
| 65 | 61 | 359 | 621 | 393 | 560 | 681 | 5 |
| 66 | 62 | 340 | 590 | 424 | 560 | 712 | 6 |
| 67 | 63 | 471 | 636 | 378 | 590 | 863 | 6 |
| 68 | 64 | 333 | 530 | 393 | 560 | 727 | 10 |
| 69 | 65 | 446 | 560 | 439 | 575 | 681 | 9 |
| 70 | 66 | 312 | 515 | 424 | 560 | 696 | 11 |
| 71 | 67 | 404 | 681 | 424 | 575 | 742 | 3 |
| 72 | 68 | 290 | 424 | 454 | 621 | 712 | 15 |
| 73 | 69 | 451 | 606 | 318 | 636 | 803 | 8 |
| 74 | 70 | 367 | 500 | 439 | 590 | 681 | 12 |
| 75 | 71 | 380 | 409 | 287 | 530 | 606 | 12 |
| 76 | 72 | 427 | 272 | 45 | 454 | 666 | 12 |
| 77 | 73 | 361 | 469 | 393 | 621 | 772 | 12 |
| 78 | 74 | 342 | 863 | 424 | 575 | 666 | 0 |

Pages whose observed agreement exceeded every shuffle: p14 (obs 772 vs shuffled max 651), p19 (obs 696 vs shuffled max 681), p28* (obs 757 vs shuffled max 712), p29 (obs 742 vs shuffled max 727), p51 (obs 727 vs shuffled max 696), p52 (obs 772 vs shuffled max 742), p59 (obs 848 vs shuffled max 696), p74 (obs 863 vs shuffled max 666).


## S2 — cross-page continuity scale

Facing-edge trail alignments (right-edge trails of one scan against
left-edge trails of another, by y-interval overlap).

| Population | Pairs | Alignments | Alignments per pair (milli) |
|---|---|---|---|
| consecutive scans | 77 | 96 | 1246 |
| non-adjacent pairs (seeded sample) | 200 | 162 | 810 |

Consecutive pairs with at least one alignment: 40 of 77. Non-adjacent pairs with at least one: 75 of 200.

Caveat carried from the trail catalog: modern scan adjacency is not
asserted to be original screenfold order, and edge trails are a
property of the physical strip and of how it was photographed. This
scale says how consecutive pairs compare with unrelated pairs on this
measurement — nothing more, and nothing is concluded from it.
