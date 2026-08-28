# Dresden discovery sweep — ranked catalogs, whole codex

Run: `python3 analysis/dresden_discover.py` — deterministic, exact.
Receipts: `data/dresden/discovery_receipts.json`. Companion verdicts:
`docs/DRESDEN_MACHINE.md`. Mode: DISCOVERY (extract structure and rank
instances; claim strength stays labeled — coordinates and distances are
MEASURED, interpretations are HYPOTHESIS until they pass a gate).

**9 exact checks, 0 failures.**

## D1 — Recurrence catalog (codex-wide, all-pairs)

7834 glyph cells; 4713 directed near-edges at the data-derived exact threshold L1 <= 205 (lower quartile of cross-page nearest-neighbour distances); 21 clusters of size >= 4.

Top 16 clusters (size, page reach, sample coordinates) — crops in `demo/dresden_recurrence_clusters.png`, one cluster per row:

| # | Size | Pages reached | Example (scan: y0,x0) |
|---|---|---|---|
| 1 | 854 | 1,2,3,4,5,6,7,8,9,10,11,12… | scan 1: 1087,267 |
| 2 | 667 | 1,2,3,4,5,6,7,8,9,10,11,12… | scan 1: 205,414 |
| 3 | 10 | 3,7,27,28**,46,52,67,72 | scan 3: 442,410 |
| 4 | 10 | 24,34,38,40,47,51,57,59,68 | scan 24: 896,326 |
| 5 | 9 | 14,21,22,30,32,44,52,53,55 | scan 14: 959,262 |
| 6 | 8 | 2,14,28**,32,33,35,37,55 | scan 2: 935,0 |
| 7 | 8 | 6,9,15,43,45,50,51,62 | scan 6: 308,521 |
| 8 | 8 | 18,28*,54,57,59,65,66,67 | scan 18: 858,572 |
| 9 | 7 | 1,3,4,18,45,52,64 | scan 1: 484,513 |
| 10 | 7 | 3,7,13,28**,28***,54 | scan 3: 864,582 |
| 11 | 6 | 5,14,26,45,50,65 | scan 5: 423,214 |
| 12 | 5 | 5,18,24,25,67 | scan 5: 308,384 |
| 13 | 5 | 23,25,39,41,70 | scan 23: 122,285 |
| 14 | 4 | 3,37,40,46 | scan 3: 770,7 |
| 15 | 4 | 4,13,18,21 | scan 4: 244,183 |
| 16 | 4 | 6,13,35,72 | scan 6: 83,478 |

Strongest single cross-page code identities (top 12):

| Query scan/page (y0,x0) | Match scan/page (y0,x0) | L1 |
|---|---|---|
| 9/p9 (927,667) | 48/p45 (176,322) | 0 |
| 10/p10 (578,258) | 45/p42 (595,293) | 0 |
| 21/p21 (189,336) | 35/p32 (393,219) | 0 |
| 22/p22 (364,111) | 54/p51 (263,364) | 0 |
| 24/p24 (1175,504) | 54/p51 (639,478) | 0 |
| 35/p32 (393,219) | 21/p21 (189,336) | 0 |
| 45/p42 (595,293) | 10/p10 (578,258) | 0 |
| 48/p45 (176,322) | 9/p9 (927,667) | 0 |
| 49/p46 (906,86) | 65/p61 (1139,639) | 0 |
| 54/p51 (263,364) | 22/p22 (364,111) | 0 |
| 54/p51 (639,478) | 24/p24 (1175,504) | 0 |
| 55/p52 (563,188) | 60/p57 (1193,503) | 0 |

## D2 — Path gallery (all 78 pages)

Overlays: `data/dresden/derived/paths/scanNN_path.jpg` (luminance-ordered tour, first 12 stations numbered). Pages ranked by tour coherence (permutation rank, lower = more ordered than chance). Note: this ranking is an exploratory pointer from the first-generation path machinery; see DRESDEN_TRAILS.md for the current trail machinery and RULES_OF_EXPLORATION.md for status vocabulary (all interpretive questions OPEN).

Most-coherent pages: scan 1 (p1, rank 0/999), scan 2 (p2, rank 0/999), scan 3 (p3, rank 0/999), scan 4 (p4, rank 0/999), scan 5 (p5, rank 0/999), scan 8 (p8, rank 0/999), scan 9 (p9, rank 0/999), scan 13 (p13, rank 0/999)

## D3 — Figure-dressing catalog

119 large-figure regions detected codex-wide; 2124 interior-element -> glyph-cell code matches collected. Top pairs (crops in `demo/dresden_dressing_pairs.png`):

| Scan/page | Figure (y0,x0) | Interior elem (y0,x0) | Matched glyph (y0,x0) | L1 |
|---|---|---|---|---|
| 69/p65 | 435,465 | 509,521 | 81,464 | 301 |
| 25/p25 | 651,129 | 725,520 | 346,94 | 345 |
| 4/p4 | 44,196 | 96,197 | 161,114 | 373 |
| 65/p61 | 281,433 | 505,533 | 894,330 | 379 |
| 28/p28 | 360,233 | 506,463 | 1093,240 | 416 |
| 73/p69 | 12,0 | 1271,222 | 0,21 | 436 |
| 65/p61 | 281,433 | 347,515 | 751,422 | 440 |
| 28/p28 | 752,182 | 755,192 | 142,447 | 458 |
| 32/p29 | 379,92 | 504,297 | 703,0 | 482 |
| 65/p61 | 281,433 | 443,467 | 876,263 | 485 |
| 25/p25 | 651,129 | 678,338 | 276,456 | 491 |
| 47/p44 | 210,260 | 371,334 | 604,438 | 511 |
| 4/p4 | 44,196 | 63,285 | 568,9 | 514 |
| 25/p25 | 651,129 | 803,352 | 578,419 | 517 |
| 65/p61 | 281,433 | 473,506 | 1140,524 | 518 |

## D4 — Dot topology census (hollow vs solid)

Codex totals: **10685 hollow** (ring-topology) vs **23725 solid** dots. Overlays for every page: `data/dresden/derived/dots/` (hollow = cyan, solid = orange). Pages with the largest hollow-dot populations — the pages richest in open (ring-topology) marks — morphology only; the researcher's stitching hypothesis is tested separately, never assumed:

| Scan | Page | Hollow | Solid |
|---|---|---|---|
| 76 | 72 | 268 | 489 |
| 75 | 71 | 250 | 382 |
| 50 | 47 | 232 | 392 |
| 51 | 48 | 204 | 356 |
| 44 | 41 | 191 | 367 |
| 53 | 50 | 188 | 312 |
| 68 | 64 | 187 | 351 |
| 2 | 2 | 187 | 500 |
| 35 | 32 | 176 | 384 |
| 52 | 49 | 174 | 362 |

## D5 — Tonal band maps

Exact quantile-band structure maps for every page: `data/dresden/derived/bands/scanNN_bands.png` (5 bands, darkest -> brightest). These are the honest 'underlying layers' renders: each band is an exact order-statistic partition of the page's own luma.

## D6 — Opportunity index (every page, no silent passes)

| Scan | Page | Cells | Raw comps | Figures | Hollow | Solid | Path rank | Best cross-page L1 |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 130 | 2782 | 1 | 33 | 72 | 0 | 18 |
| 2 | 2 | 111 | 6260 | 2 | 187 | 500 | 0 | 19 |
| 3 | 3 | 152 | 4107 | 1 | 62 | 164 | 0 | 68 |
| 4 | 4 | 106 | 5720 | 3 | 141 | 273 | 0 | 83 |
| 5 | 5 | 92 | 5120 | 1 | 124 | 281 | 0 | 15 |
| 6 | 6 | 83 | 6181 | 1 | 141 | 299 | 7 | 3 |
| 7 | 7 | 102 | 5676 | 1 | 102 | 272 | 3 | 1 |
| 8 | 8 | 88 | 5401 | 1 | 138 | 282 | 0 | 15 |
| 9 | 9 | 106 | 5300 | 2 | 126 | 299 | 0 | 0 |
| 10 | 10 | 82 | 5325 | 2 | 123 | 306 | 82 | 0 |
| 11 | 11 | 64 | 5772 | 1 | 132 | 312 | 602 | 11 |
| 12 | 12 | 56 | 6218 | 2 | 131 | 295 | 64 | 4 |
| 13 | 13 | 89 | 6404 | 1 | 130 | 302 | 0 | 6 |
| 14 | 14 | 102 | 6371 | 1 | 116 | 272 | 0 | 1 |
| 15 | 15 | 115 | 6125 | 1 | 124 | 257 | 0 | 1 |
| 16 | 16 | 86 | 5784 | 2 | 112 | 233 | 0 | 78 |
| 17 | 17 | 92 | 4832 | 1 | 129 | 203 | 224 | 59 |
| 18 | 18 | 101 | 5174 | 1 | 101 | 227 | 0 | 5 |
| 19 | 19 | 75 | 5833 | 1 | 151 | 290 | 0 | 8 |
| 20 | 20 | 70 | 5630 | 1 | 116 | 252 | 27 | 6 |
| 21 | 21 | 93 | 5829 | 2 | 166 | 297 | 36 | 0 |
| 22 | 22 | 110 | 5162 | 1 | 153 | 304 | 1 | 0 |
| 23 | 23 | 120 | 5576 | 1 | 173 | 275 | 0 | 7 |
| 24 | 24 | 188 | 4660 | 1 | 148 | 298 | 0 | 0 |
| 25 | 25 | 102 | 5174 | 3 | 138 | 297 | 441 | 91 |
| 26 | 26 | 87 | 5549 | 2 | 120 | 231 | 35 | 106 |
| 27 | 27 | 68 | 5087 | 2 | 111 | 212 | 92 | 89 |
| 28 | 28 | 109 | 5031 | 4 | 153 | 272 | 1 | 116 |
| 29 | 28* | 116 | 3846 | 1 | 81 | 124 | 0 | 106 |
| 30 | 28** | 97 | 3997 | 1 | 63 | 120 | 0 | 88 |
| 31 | 28*** | 37 | 2114 | 2 | 33 | 49 | 378 | 98 |
| 32 | 29 | 115 | 6154 | 2 | 139 | 301 | 1 | 72 |
| 33 | 30 | 92 | 5259 | 2 | 166 | 353 | 0 | 1 |
| 34 | 31 | 95 | 5822 | 2 | 169 | 439 | 186 | 23 |
| 35 | 32 | 74 | 6093 | 2 | 176 | 384 | 0 | 0 |
| 36 | 33 | 83 | 5940 | 1 | 166 | 355 | 175 | 92 |
| 37 | 34 | 103 | 6627 | 1 | 139 | 385 | 0 | 38 |
| 38 | 35 | 45 | 5044 | 2 | 135 | 240 | 63 | 162 |
| 39 | 36 | 110 | 6093 | 1 | 158 | 356 | 0 | 109 |
| 40 | 37 | 113 | 6503 | 1 | 146 | 361 | 12 | 81 |
| 41 | 38 | 71 | 5829 | 1 | 158 | 290 | 9 | 11 |
| 42 | 39 | 63 | 5540 | 2 | 125 | 361 | 0 | 6 |
| 43 | 40 | 90 | 5286 | 3 | 104 | 377 | 10 | 3 |
| 44 | 41 | 63 | 5697 | 1 | 191 | 367 | 209 | 26 |
| 45 | 42 | 94 | 6665 | 1 | 173 | 368 | 2 | 0 |
| 46 | 43 | 148 | 5356 | 1 | 148 | 413 | 1 | 9 |
| 47 | 44 | 128 | 4923 | 2 | 139 | 400 | 2 | 1 |
| 48 | 45 | 118 | 4064 | 1 | 121 | 236 | 69 | 0 |
| 49 | 46 | 140 | 5842 | 2 | 117 | 310 | 24 | 0 |
| 50 | 47 | 99 | 5611 | 1 | 232 | 392 | 0 | 13 |
| 51 | 48 | 98 | 5676 | 1 | 204 | 356 | 0 | 2 |
| 52 | 49 | 76 | 5860 | 1 | 174 | 362 | 3 | 59 |
| 53 | 50 | 100 | 5451 | 1 | 188 | 312 | 5 | 36 |
| 54 | 51 | 155 | 3855 | 2 | 120 | 266 | 0 | 0 |
| 55 | 52 | 171 | 3574 | 1 | 123 | 359 | 0 | 0 |
| 56 | 53 | 116 | 4515 | 4 | 137 | 341 | 17 | 2 |
| 57 | 54 | 145 | 3902 | 1 | 119 | 312 | 5 | 4 |
| 58 | 55 | 128 | 4139 | 1 | 140 | 342 | 0 | 2 |
| 59 | 56 | 117 | 3484 | 2 | 94 | 251 | 15 | 1 |
| 60 | 57 | 107 | 3848 | 1 | 136 | 291 | 16 | 0 |
| 61 | 58 | 105 | 4160 | 1 | 152 | 271 | 0 | 9 |
| 62 | 59 | 154 | 3909 | 1 | 155 | 363 | 0 | 10 |
| 63 | 60 | 53 | 5329 | 1 | 114 | 294 | 31 | 97 |
| 64 | 60* | 51 | 2157 | 1 | 27 | 70 | 494 | 7 |
| 65 | 61 | 142 | 6166 | 3 | 139 | 371 | 0 | 0 |
| 66 | 62 | 110 | 5049 | 3 | 131 | 370 | 0 | 4 |
| 67 | 63 | 164 | 4812 | 2 | 166 | 403 | 0 | 20 |
| 68 | 64 | 179 | 4296 | 1 | 187 | 351 | 0 | 12 |
| 69 | 65 | 75 | 5525 | 3 | 121 | 320 | 3 | 21 |
| 70 | 66 | 75 | 6292 | 1 | 159 | 381 | 2 | 22 |
| 71 | 67 | 74 | 5368 | 3 | 123 | 400 | 88 | 6 |
| 72 | 68 | 52 | 5033 | 1 | 137 | 362 | 41 | 22 |
| 73 | 69 | 48 | 4141 | 1 | 123 | 302 | 412 | 9 |
| 74 | 70 | 113 | 3842 | 2 | 122 | 357 | 230 | 1 |
| 75 | 71 | 126 | 4970 | 1 | 250 | 382 | 0 | 18 |
| 76 | 72 | 90 | 6421 | 1 | 268 | 489 | 0 | 4 |
| 77 | 73 | 99 | 3693 | 1 | 147 | 336 | 218 | 7 |
| 78 | 74 | 38 | 3680 | 1 | 69 | 153 | 137 | 35 |

