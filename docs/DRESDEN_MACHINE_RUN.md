# The glyph machine on the Dresden Codex scan set

Run: `python3 analysis/dresden_run.py` — deterministic, integer-exact.
Receipts: `data/dresden/machine_receipts.json` (hash-chained).

**636 exact checks, 0 failures.**

## §1 Machine self-tests (synthetic fixtures, exact expectations)

## §2 Full-codex pass (78 scans) — segmentation + C3 path test
Glyph cells across the codex: **7834** (params: Otsu ink, dilate 2, area window [120, 12000]).

C3 — luminance-path permutation test, per page: observed L1 tour of the brightest-first cell ordering vs 999 seeded shuffles. Exact p-value = (rank+1)/1000; p <= 0.05 requires rank+1 <= 50.

| Scan | Page | Cells | Observed tour | Shuffles <= observed / 999 |
|---|---|---|---|---|
| 1 | 1 | 130 | 64840 | 0 |
| 2 | 2 | 111 | 54460 | 0 |
| 3 | 3 | 152 | 71159 | 0 |
| 4 | 4 | 106 | 47784 | 0 |
| 5 | 5 | 92 | 41057 | 0 |
| 6 | 6 | 83 | 47274 | 7 |
| 7 | 7 | 102 | 51218 | 3 |
| 8 | 8 | 88 | 43336 | 0 |
| 9 | 9 | 106 | 49570 | 0 |
| 10 | 10 | 82 | 46667 | 82 |
| 11 | 11 | 64 | 40535 | 602 |
| 12 | 12 | 56 | 31901 | 64 |
| 13 | 13 | 89 | 41106 | 0 |
| 14 | 14 | 102 | 47163 | 0 |
| 15 | 15 | 115 | 53683 | 0 |
| 16 | 16 | 86 | 36606 | 0 |
| 17 | 17 | 92 | 56157 | 224 |
| 18 | 18 | 101 | 44722 | 0 |
| 19 | 19 | 75 | 31142 | 0 |
| 20 | 20 | 70 | 39041 | 27 |
| 21 | 21 | 93 | 54772 | 36 |
| 22 | 22 | 110 | 60717 | 1 |
| 23 | 23 | 120 | 61895 | 0 |
| 24 | 24 | 188 | 74197 | 0 |
| 25 | 25 | 102 | 59110 | 441 |
| 26 | 26 | 87 | 51603 | 35 |
| 27 | 27 | 68 | 40352 | 92 |
| 28 | 28 | 109 | 53861 | 1 |
| 29 | 28* | 116 | 52547 | 0 |
| 30 | 28** | 97 | 45988 | 0 |
| 31 | 28*** | 37 | 22425 | 378 |
| 32 | 29 | 115 | 55102 | 1 |
| 33 | 30 | 92 | 43850 | 0 |
| 34 | 31 | 95 | 58567 | 186 |
| 35 | 32 | 74 | 30638 | 0 |
| 36 | 33 | 83 | 40906 | 175 |
| 37 | 34 | 103 | 43012 | 0 |
| 38 | 35 | 45 | 24436 | 63 |
| 39 | 36 | 110 | 51464 | 0 |
| 40 | 37 | 113 | 58160 | 12 |
| 41 | 38 | 71 | 32985 | 9 |
| 42 | 39 | 63 | 30860 | 0 |
| 43 | 40 | 90 | 47449 | 10 |
| 44 | 41 | 63 | 35589 | 209 |
| 45 | 42 | 94 | 42019 | 2 |
| 46 | 43 | 148 | 71546 | 1 |
| 47 | 44 | 128 | 60221 | 2 |
| 48 | 45 | 118 | 61258 | 69 |
| 49 | 46 | 140 | 68219 | 24 |
| 50 | 47 | 99 | 43342 | 0 |
| 51 | 48 | 98 | 34033 | 0 |
| 52 | 49 | 76 | 33501 | 3 |
| 53 | 50 | 100 | 39813 | 5 |
| 54 | 51 | 155 | 69604 | 0 |
| 55 | 52 | 171 | 80171 | 0 |
| 56 | 53 | 116 | 62412 | 17 |
| 57 | 54 | 145 | 72788 | 5 |
| 58 | 55 | 128 | 65259 | 0 |
| 59 | 56 | 117 | 60186 | 15 |
| 60 | 57 | 107 | 56699 | 16 |
| 61 | 58 | 105 | 49746 | 0 |
| 62 | 59 | 154 | 64989 | 0 |
| 63 | 60 | 53 | 29368 | 31 |
| 64 | 60* | 51 | 34431 | 494 |
| 65 | 61 | 142 | 68861 | 0 |
| 66 | 62 | 110 | 50355 | 0 |
| 67 | 63 | 164 | 81644 | 0 |
| 68 | 64 | 179 | 89107 | 0 |
| 69 | 65 | 75 | 39264 | 3 |
| 70 | 66 | 75 | 38005 | 2 |
| 71 | 67 | 74 | 37651 | 88 |
| 72 | 68 | 52 | 29494 | 41 |
| 73 | 69 | 48 | 34408 | 412 |
| 74 | 70 | 113 | 66246 | 230 |
| 75 | 71 | 126 | 63034 | 0 |
| 76 | 72 | 90 | 43118 | 0 |
| 77 | 73 | 99 | 57846 | 218 |
| 78 | 74 | 38 | 20632 | 137 |

Pages at p <= 0.05: **60 of 78** (chance expectation at the 5% level: ~3). Verdict on C3 is stated in docs/DRESDEN_MACHINE.md from these numbers.

### C3 control — blank pages (no glyphs, pseudo-cell grid)

| Scan | Page | Pseudo-cells | Observed tour | Shuffles <= / 999 |
|---|---|---|---|---|
| 29 | 28* | 112 | 48695 | 0 |
| 30 | 28** | 112 | 43545 | 0 |
| 31 | 28*** | 112 | 42960 | 0 |
| 64 | 60* | 112 | 48185 | 0 |

Blank-page control ranks: [0, 0, 0, 0]. If these are also << 50, the short tours on inscribed pages are explained by substrate-luminance autocorrelation (illumination and plaster tone vary smoothly across any page), and carry no evidence of a designed path.

## §3 C1/C2 — glyph internal codes and their recurrence (Venus pages)
Query page scan 49 (Förstemann 46): 140 cells. Candidate pool: 373 cells on scans [50, 51, 52, 53] (pages 47-50).

Median nearest-neighbour signature distance (milli-L1 over 12 rings): same page **419**, cross page **404**.

Top 10 cross-page code matches (exact distances):

| Query box (y0,y1,x0,x1) | Match scan/page | Match box | L1 dist |
|---|---|---|---|
| (647,662,510,525) | 52 / 49 | (369,382,446,460) | 90 |
| (932,947,260,273) | 52 / 49 | (87,100,561,576) | 99 |
| (906,920,86,100) | 50 / 47 | (945,960,673,684) | 104 |
| (106,124,429,444) | 52 / 49 | (82,104,467,484) | 131 |
| (1035,1049,321,335) | 51 / 48 | (945,959,118,133) | 138 |
| (147,175,462,483) | 52 / 49 | (113,141,158,209) | 180 |
| (784,796,85,104) | 50 / 47 | (146,161,97,116) | 185 |
| (1149,1170,286,307) | 53 / 50 | (159,174,561,576) | 192 |
| (191,208,390,407) | 52 / 49 | (203,219,571,586) | 195 |
| (709,722,436,461) | 53 / 50 | (171,184,161,178) | 195 |

Null control: nearest-neighbour distance to 240 seeded random-placement signatures on the same candidate pages — median **543** (vs 404 for real cells). Interpretation in the doc, from the numbers.

## §4 C4 — locating the photographed column (exact template search)
Query: researcher's photographed column (pinned decimation, receipts in data/dresden/queries/). Method: median-centred integer SAD over all 78 scans at 5 template scales, nearest-neighbour geometry casts only. Top 8 (mean-SAD per pixel, scan, template width, x, y):

- mean-SAD 33 — scan 29 (page 28*), tw=26, at (6, 91)
- mean-SAD 33 — scan 29 (page 28*), tw=38, at (6, 55)
- mean-SAD 33 — scan 29 (page 28*), tw=54, at (5, 9)
- mean-SAD 33 — scan 31 (page 28***), tw=26, at (4, 89)
- mean-SAD 34 — scan 29 (page 28*), tw=32, at (6, 70)
- mean-SAD 34 — scan 29 (page 28*), tw=46, at (6, 38)
- mean-SAD 34 — scan 30 (page 28**), tw=26, at (7, 4)
- mean-SAD 34 — scan 31 (page 28***), tw=32, at (4, 72)

**4 of the top 4 hits are blank pages** — the matcher found low-contrast fits, not structure. NEGATIVE: the photographed column is not located in this scan set at these scales. Its layout (single full-column figure, no register rules) matches no Dresden section; a Madrid Codex origin is a HYPOTHESIS for the researcher to check, not a finding.

