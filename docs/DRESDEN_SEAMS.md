# DRESDEN_SEAMS — repair-seam probes, codex-wide (NODE-DRE02)

Run: `python3 analysis/dresden_seams.py`; receipts
`data/dresden/seam_receipts.json`; panels `data/dresden/derived/seams/`.

**4 exact checks, 0 failures.**

## P1 — requantization fingerprint

Total flagged blocks across all 78 scans: **0**.
As on the Archimedes sensor data, the fingerprint statistic recorded a NULL on
these continuous-tone JPEG-decoded scans — recorded, not buried. Mixed
processing histories inside a page are not detected by this probe here.

## P2 — block-median discontinuity (physical seam candidates)

Per-page threshold: exact order statistic at 990 milli of the page's own
neighbour differences, floored at 24 luma steps. Candidates are block
boundaries, coordinates in 16 px block units (x16 for pixels).

| Scan | Page | fp step | fp flags | median thr | seam candidates |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 0 | 155 | 72 |
| 2 | 2 | 1 | 0 | 98 | 72 |
| 3 | 3 | 1 | 0 | 116 | 72 |
| 4 | 4 | 1 | 0 | 118 | 74 |
| 5 | 5 | 1 | 0 | 124 | 72 |
| 6 | 6 | 1 | 0 | 119 | 73 |
| 7 | 7 | 1 | 0 | 103 | 73 |
| 8 | 8 | 1 | 0 | 124 | 71 |
| 9 | 9 | 1 | 0 | 114 | 71 |
| 10 | 10 | 1 | 0 | 114 | 71 |
| 11 | 11 | 1 | 0 | 120 | 71 |
| 12 | 12 | 1 | 0 | 107 | 73 |
| 13 | 13 | 1 | 0 | 114 | 73 |
| 14 | 14 | 1 | 0 | 113 | 71 |
| 15 | 15 | 1 | 0 | 119 | 72 |
| 16 | 16 | 1 | 0 | 120 | 71 |
| 17 | 17 | 1 | 0 | 126 | 71 |
| 18 | 18 | 1 | 0 | 152 | 71 |
| 19 | 19 | 1 | 0 | 103 | 74 |
| 20 | 20 | 1 | 0 | 117 | 71 |
| 21 | 21 | 1 | 0 | 129 | 74 |
| 22 | 22 | 1 | 0 | 140 | 71 |
| 23 | 23 | 1 | 0 | 120 | 72 |
| 24 | 24 | 1 | 0 | 138 | 71 |
| 25 | 25 | 1 | 0 | 160 | 71 |
| 26 | 26 | 1 | 0 | 114 | 71 |
| 27 | 27 | 1 | 0 | 146 | 73 |
| 28 | 28 | 1 | 0 | 106 | 73 |
| 29 | 28* | 1 | 0 | 74 | 73 |
| 30 | 28** | 1 | 0 | 68 | 74 |
| 31 | 28*** | 1 | 0 | 111 | 71 |
| 32 | 29 | 1 | 0 | 125 | 73 |
| 33 | 30 | 1 | 0 | 128 | 71 |
| 34 | 31 | 1 | 0 | 125 | 73 |
| 35 | 32 | 1 | 0 | 118 | 73 |
| 36 | 33 | 1 | 0 | 112 | 73 |
| 37 | 34 | 1 | 0 | 109 | 72 |
| 38 | 35 | 1 | 0 | 113 | 74 |
| 39 | 36 | 1 | 0 | 112 | 72 |
| 40 | 37 | 1 | 0 | 131 | 71 |
| 41 | 38 | 1 | 0 | 107 | 72 |
| 42 | 39 | 1 | 0 | 102 | 74 |
| 43 | 40 | 1 | 0 | 109 | 73 |
| 44 | 41 | 1 | 0 | 114 | 71 |
| 45 | 42 | 1 | 0 | 114 | 72 |
| 46 | 43 | 1 | 0 | 135 | 76 |
| 47 | 44 | 1 | 0 | 127 | 71 |
| 48 | 45 | 1 | 0 | 153 | 73 |
| 49 | 46 | 1 | 0 | 157 | 75 |
| 50 | 47 | 1 | 0 | 102 | 71 |
| 51 | 48 | 1 | 0 | 98 | 72 |
| 52 | 49 | 1 | 0 | 95 | 74 |
| 53 | 50 | 1 | 0 | 102 | 72 |
| 54 | 51 | 1 | 0 | 118 | 73 |
| 55 | 52 | 1 | 0 | 116 | 77 |
| 56 | 53 | 1 | 0 | 114 | 71 |
| 57 | 54 | 1 | 0 | 122 | 73 |
| 58 | 55 | 1 | 0 | 115 | 75 |
| 59 | 56 | 1 | 0 | 139 | 72 |
| 60 | 57 | 1 | 0 | 120 | 75 |
| 61 | 58 | 1 | 0 | 116 | 72 |
| 62 | 59 | 1 | 0 | 131 | 72 |
| 63 | 60 | 1 | 0 | 124 | 73 |
| 64 | 60* | 1 | 0 | 144 | 74 |
| 65 | 61 | 1 | 0 | 156 | 71 |
| 66 | 62 | 1 | 0 | 142 | 71 |
| 67 | 63 | 1 | 0 | 141 | 71 |
| 68 | 64 | 1 | 0 | 132 | 72 |
| 69 | 65 | 1 | 0 | 127 | 71 |
| 70 | 66 | 1 | 0 | 157 | 71 |
| 71 | 67 | 1 | 0 | 142 | 73 |
| 72 | 68 | 1 | 0 | 131 | 71 |
| 73 | 69 | 1 | 0 | 136 | 72 |
| 74 | 70 | 1 | 0 | 152 | 75 |
| 75 | 71 | 1 | 0 | 117 | 72 |
| 76 | 72 | 1 | 0 | 104 | 72 |
| 77 | 73 | 1 | 0 | 128 | 74 |
| 78 | 74 | 1 | 0 | 143 | 74 |

Panels (green = vertical boundary, magenta = horizontal) for the six
highest-candidate pages: scan 55 (p52), scan 46 (p43), scan 49 (p46), scan 58 (p55), scan 60 (p57), scan 74 (p70).

Reading note: median discontinuities mark tonal steps — repairs, patch
edges, exposed backing, and also legitimate painted boundaries (red
frame lines). CODICOLOGICAL confirmation (which candidates are repairs)
needs the physical-object literature or higher-res captures; this map
is the candidate enumeration the node's gate asks for.
