# Dot morphology — measured, unlabelled

Run: `python3 analysis/dresden_dots.py`; receipts
`data/dresden/dot_receipts.json`; panel `demo/dresden_dot_morphology.png`.

**6 exact checks, 0 failures.**

Detector rule (stated, assumption-free): connected ink components with
area 20–900 px and bbox aspect >= 500 milli are 'round marks'; a mark
is OPEN if it encloses at least one 4-connected background component
not touching its border, FILLED otherwise. Nothing is called a stitch
hole, a numeral, or a decoration by this script.

Population: **34410 round marks** — 10685 open, 23725 filled.

## Q1 — do the two classes separate on morphology?

| Attribute | Open median | Filled median | Open marks inside the filled IQR (milli) |
|---|---|---|---|
| area | 98 | 39 | 325 |
| aspect | 772 | 777 | 549 |
| fill | 375 | 439 | 560 |
| thickness | 1510 | 1000 | 408 |

Reading: a high overlap figure means the classes are one continuum cut
by the topology test; a low one means they are morphologically distinct
populations. Both are reported without a verdict.

## Q2 — spacing regularity per page and class

Median nearest-neighbour distance and its dispersion ((p75-p25)*1000/median; small = regular, large = clustered).

| Class | Pages measured | Median NN distance (median over pages) | Median dispersion |
|---|---|---|---|
| open | 78 | 40 | 806 |
| filled | 78 | 24 | 857 |

Per-page detail (open marks, most regular first):

| Scan | Page | Open marks | Median NN | Dispersion |
|---|---|---|---|---|
| 9 | 9 | 126 | 43 | 488 |
| 25 | 25 | 138 | 45 | 533 |
| 11 | 11 | 132 | 44 | 613 |
| 58 | 55 | 140 | 52 | 615 |
| 12 | 12 | 131 | 47 | 617 |
| 56 | 53 | 137 | 45 | 622 |
| 52 | 49 | 174 | 35 | 628 |
| 45 | 42 | 173 | 38 | 631 |
| 76 | 72 | 268 | 30 | 633 |
| 31 | 28*** | 33 | 55 | 636 |
| 35 | 32 | 176 | 40 | 650 |
| 13 | 13 | 130 | 43 | 651 |
| 53 | 50 | 188 | 32 | 656 |
| 40 | 37 | 146 | 39 | 666 |
| 43 | 40 | 104 | 48 | 666 |

## Q3 — pages whose open-mark morphology most resembles the located p69 column

Reference profile (median area / aspect / fill / thickness) taken from
the 19 open marks inside the located column on p69: [74, 833, 446, 1727].

| Rank | Scan | Page | Open marks | L1 distance to reference | Profile |
|---|---|---|---|---|---|
| 1 | 61 | 58 | 152 | 100 | [90, 800, 474, 1750] |
| 2 | 74 | 70 | 122 | 158 | [82, 800, 443, 1613] |
| 3 | 73 | 69 | 123 | 177 | [100, 750, 418, 1687] |
| 4 | 67 | 63 | 166 | 181 | [101, 788, 489, 1661] |
| 5 | 66 | 62 | 131 | 184 | [103, 777, 414, 1660] |
| 6 | 48 | 45 | 121 | 198 | [117, 750, 375, 1728] |
| 7 | 9 | 9 | 126 | 208 | [117, 803, 357, 1681] |
| 8 | 59 | 56 | 94 | 213 | [101, 782, 384, 1800] |
| 9 | 60 | 57 | 136 | 217 | [100, 777, 438, 1854] |
| 10 | 62 | 59 | 155 | 227 | [76, 800, 522, 1611] |
| 11 | 24 | 24 | 148 | 241 | [84, 777, 445, 1553] |
| 12 | 23 | 23 | 173 | 251 | [94, 738, 399, 1638] |
| 13 | 75 | 71 | 250 | 256 | [92, 785, 474, 1565] |
| 14 | 17 | 17 | 129 | 261 | [126, 785, 311, 1701] |
| 15 | 53 | 50 | 188 | 261 | [112, 800, 349, 1634] |

Status: MEASURED. Whether open marks are preparation holes, a mark
class with a scribal function, or a byproduct of pigment loss is not
decided here — the morphology, spacing and recurrence figures are the
material for that question (docs/RULES_OF_EXPLORATION.md).
