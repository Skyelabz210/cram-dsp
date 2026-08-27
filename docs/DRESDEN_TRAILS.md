# White trails — gradient-to-white filaments, whole codex

Run: `python3 analysis/dresden_trails.py`; receipts
`data/dresden/trail_receipts.json`; per-page trail overlays
`data/dresden/derived/trails/scanNN_trails.jpg`.

**10 exact checks, 0 failures.**

Definition (named transform, fixed parameters): the trail field is the
LOCAL brightness excess — luma minus the pixel's own 16 px block-median
substrate — so trails are what is brighter than their surroundings,
independent of page lighting. A TRAIL is a connected component of that
field at >= 14 luma steps (ink excluded, 2-step gap bridging) that is
long (>= 60 px) and thin relative to its length (mean thickness <= 24,
length >= 3x thickness). It ASCENDS ('gradient to white') if any pixel
reaches >= 28 above local substrate. The glyph sequence of a trail is
the glyphs within L1 40 px of its centreline, in arc order. Every
number is an exact integer function of the scan.

Observation shipped as measured: the four BLANK pages rank among the
most trail-rich — trails are substrate/fiber phenomena that exist
without writing. The glyph-sequence catalog below therefore draws from
the trail-richest INSCRIBED pages; what a trail's interaction with
glyphs means stays an open exploration question.

## The machine's ranking — best trail pages

| Rank | Scan | Page | Trails | Ascending | Score (asc. length px) |
|---|---|---|---|---|---|
| 1 | 74 | 70 | 44 | 43 | 4166 |
| 2 | 54 | 51 | 36 | 35 | 3281 |
| 3 | 40 | 37 | 33 | 33 | 3270 |
| 4 | 55 | 52 | 38 | 35 | 3237 |
| 5 | 77 | 73 | 33 | 31 | 3209 |
| 6 | 39 | 36 | 28 | 28 | 2961 |
| 7 | 56 | 53 | 35 | 33 | 2954 |
| 8 | 75 | 71 | 29 | 29 | 2727 |
| 9 | 58 | 55 | 27 | 27 | 2635 |
| 10 | 62 | 59 | 20 | 19 | 2612 |
| 11 | 29 | 28* | 32 | 29 | 2568 |
| 12 | 46 | 43 | 22 | 21 | 2545 |
| 13 | 57 | 54 | 31 | 28 | 2514 |
| 14 | 19 | 19 | 23 | 23 | 2478 |
| 15 | 24 | 24 | 28 | 28 | 2442 |

## Strongest-trail glyph sequences (top pages)

- **p70**: trail length 127 px, thickness 18, 22 polyline points, luma 198 -> 214 along the arc (ascending), 3 glyphs on the trail — overlay `demo/dresden_trail_p70.png`, sequence strip `demo/dresden_trailseq_p70.png`.
- **p51**: trail length 120 px, thickness 21, 20 polyline points, luma 171 -> 193 along the arc (ascending), 3 glyphs on the trail — overlay `demo/dresden_trail_p51.png`, sequence strip `demo/dresden_trailseq_p51.png`.
- **p37**: trail length 213 px, thickness 20, 36 polyline points, luma 166 -> 193 along the arc (ascending), 8 glyphs on the trail — overlay `demo/dresden_trail_p37.png`, sequence strip `demo/dresden_trailseq_p37.png`.
- **p52**: trail length 154 px, thickness 24, 26 polyline points, luma 175 -> 218 along the arc (ascending), 6 glyphs on the trail — overlay `demo/dresden_trail_p52.png`, sequence strip `demo/dresden_trailseq_p52.png`.
- **p73**: trail length 114 px, thickness 11, 19 polyline points, luma 144 -> 205 along the arc (ascending), 6 glyphs on the trail — overlay `demo/dresden_trail_p73.png`, sequence strip `demo/dresden_trailseq_p73.png`.
- **p36**: trail length 530 px, thickness 23, 89 polyline points, luma 214 -> 187 along the arc (descending-or-flat), 9 glyphs on the trail — overlay `demo/dresden_trail_p36.png`, sequence strip `demo/dresden_trailseq_p36.png`.

## Better pages for the character-matching (dressing) experiment

Machine ranking by figures x glyph cells (both must be present):

| Rank | Scan | Page | Figures | Cells |
|---|---|---|---|---|
| 1 | 56 | 53 | 4 | 116 |
| 2 | 28 | 28 | 4 | 109 |
| 3 | 65 | 61 | 3 | 142 |
| 4 | 66 | 62 | 3 | 110 |
| 5 | 67 | 63 | 2 | 164 |
| 6 | 4 | 4 | 3 | 106 |
| 7 | 54 | 51 | 2 | 155 |
| 8 | 25 | 25 | 3 | 102 |
| 9 | 49 | 46 | 2 | 140 |
| 10 | 43 | 40 | 3 | 90 |
| 11 | 47 | 44 | 2 | 128 |
| 12 | 59 | 56 | 2 | 117 |

Reading note: trail existence, arc order, and glyph sequences are
MEASURED. Whether a trail is an intentional mark, a fiber of the bark
paper, plaster loss, or sizing is a materials question — the maps give
every candidate with coordinates so that question can be asked of the
physical object. The blank-page control applies to design claims, not
to the existence or geometry of the trails.
