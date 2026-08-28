# Per-page segmentation — every page, every element, numbered and categorised

Run: `python3 analysis/dresden_segment.py`; receipts `data/dresden/segment_receipts.json`; per-page JSON in `data/dresden/segments/`; overlays in `data/dresden/derived/segments/`; codex contact sheet `demo/dresden_segments_contact.jpg`.

This is the layer the original request asked for and that was missing. The request was that each page be *carefully segmented, numbered, and grouped into common assumed categories*. `INDEX.md` delivered the numbering and the grouping; the segmentation was never built, and every later stage paid for it — figure detectors that merged a page into one blob, glyph detectors that returned three boxes for a column holding a dozen glyphs.

Categories are geometric rules only. **No meaning is assigned to any element**, and nothing here closes anything (`docs/RULES_OF_EXPLORATION.md`).

## Hierarchy

```
leaf  ->  registers  ->  zones  ->  rows  ->  cells
```

Every geometric threshold is keyed to the **leaf**, and every cut is an order statistic of the page's own ink projection — not a tuned constant.

## Four defects this stage found and fixed (receipts)

1. **Every threshold was keyed to the scan frame, not the page.** Each WDL scan carries slivers of the *adjacent leaves*, so the scan frame is roughly 20% wider than the leaf and its edges are the neighbours. `leaf_block` now finds the dark gutter and mount bands as dark-fraction peaks in the outer quarter (rows: outer fifth) and every later rule is measured inside it.

2. **Register rules were detected by component shape and returned ZERO** on scan 50, whose rules are plainly visible. A rule touches the red-brown mottling of the damaged plaster and the component becomes a blob. Replaced by `dresden.open_line` — an exact integer morphological opening by a straight line, which tests the property a rule actually has (an unbroken run) instead of a property of whatever component it happens to join.

3. **One gap threshold per zone under-splits dense writing.** The sparse upper column of scan 50 segmented cleanly while the dense lower registers came back as a handful of boxes spanning 2x3 glyph grids. Cells larger than 3/2 of the page's own median glyph cell are now re-cut at the minimum of their own projection.

4. **Red bar-and-dot numerals were invisible.** The cell pass ran on black ink alone. Folding red into the same projection merged numerals into neighbouring glyph cells, so they get their own component pass — they are isolated marks, and unlike glyphs they segment correctly that way.

## Named instrument limits (MEASURED, not closed)

- **Line-drawn figures are not separable from dense line-drawn writing at 684x1350.** Figures are emitted from two passes and labelled by provenance: `colour_mass` (applied red/blue picture areas — reliable) and `stroke_mass` (black outline masses). A discriminator was tried and *does not work*: the largest undilated stroke as a share of the mass scores **52/1000 on 402 raw strokes** for the true seated figure of p69 (scan 73) and **43/1000 on 399** for a block of merged writing on the same page. Both numbers ship with every `stroke_mass` figure so a higher-resolution capture can be tested against them.

- **`margin` fired 0 times across all 78 pages.** The category is subsumed: `leaf_block` cuts at the gutter, so a page-edge red frame lies outside the leaf by construction. Reported as zero rather than removed (`BENCHMARKS.md` section 3).

- **`panel_ground` fired 4 times.** A panel must fill 600/1000 of its own box, which is what stops the red-brown mottling being called a panel; most picture areas are carried by `figure` instead.

Codex totals: **376** figure, **11679** glyph_block, **878** numeral_bar, **4205** numeral_dot, **4** panel_ground, **273** rule_h, **137** rule_v, **0** margin.

| Scan | Page | Registers | Elements | figure | glyph_block | numeral_bar | numeral_dot | panel_ground | rule_h | rule_v | margin | hollow dots |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 19 | 3 | 8 | 0 | 8 | 0 | 0 | 0 | 0 | 3 |
| 2 | 2 | 1 | 172 | 0 | 172 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 3 | 1 | 243 | 2 | 219 | 1 | 21 | 0 | 0 | 0 | 0 | 14 |
| 4 | 4 | 1 | 258 | 4 | 174 | 20 | 60 | 0 | 0 | 0 | 0 | 22 |
| 5 | 5 | 3 | 266 | 6 | 206 | 16 | 35 | 0 | 2 | 1 | 0 | 6 |
| 6 | 6 | 3 | 249 | 6 | 201 | 10 | 30 | 0 | 2 | 0 | 0 | 6 |
| 7 | 7 | 5 | 190 | 11 | 129 | 10 | 35 | 0 | 4 | 1 | 0 | 5 |
| 8 | 8 | 3 | 172 | 7 | 127 | 12 | 23 | 0 | 2 | 1 | 0 | 2 |
| 9 | 9 | 4 | 188 | 10 | 122 | 17 | 35 | 0 | 3 | 1 | 0 | 9 |
| 10 | 10 | 4 | 162 | 7 | 95 | 12 | 42 | 0 | 3 | 3 | 0 | 1 |
| 11 | 11 | 4 | 182 | 5 | 114 | 16 | 40 | 0 | 3 | 4 | 0 | 6 |
| 12 | 12 | 3 | 198 | 4 | 154 | 15 | 21 | 0 | 2 | 2 | 0 | 7 |
| 13 | 13 | 4 | 218 | 6 | 157 | 16 | 33 | 0 | 4 | 2 | 0 | 6 |
| 14 | 14 | 5 | 221 | 6 | 155 | 10 | 43 | 0 | 5 | 2 | 0 | 9 |
| 15 | 15 | 4 | 227 | 4 | 179 | 11 | 29 | 0 | 3 | 1 | 0 | 1 |
| 16 | 16 | 5 | 137 | 10 | 97 | 7 | 15 | 1 | 5 | 2 | 0 | 4 |
| 17 | 17 | 9 | 172 | 5 | 137 | 5 | 10 | 0 | 12 | 3 | 0 | 3 |
| 18 | 18 | 3 | 227 | 8 | 160 | 10 | 46 | 0 | 2 | 1 | 0 | 5 |
| 19 | 19 | 4 | 267 | 4 | 208 | 20 | 30 | 0 | 3 | 2 | 0 | 5 |
| 20 | 20 | 4 | 243 | 3 | 173 | 14 | 46 | 0 | 3 | 4 | 0 | 4 |
| 21 | 21 | 3 | 173 | 7 | 113 | 21 | 29 | 0 | 2 | 1 | 0 | 5 |
| 22 | 22 | 4 | 278 | 6 | 190 | 13 | 65 | 0 | 3 | 1 | 0 | 9 |
| 23 | 23 | 4 | 211 | 3 | 147 | 16 | 41 | 0 | 4 | 0 | 0 | 5 |
| 24 | 24 | 2 | 328 | 2 | 237 | 9 | 79 | 0 | 1 | 0 | 0 | 10 |
| 25 | 25 | 1 | 280 | 4 | 250 | 5 | 21 | 0 | 0 | 0 | 0 | 7 |
| 26 | 26 | 1 | 122 | 0 | 113 | 0 | 8 | 0 | 0 | 1 | 0 | 1 |
| 27 | 27 | 1 | 252 | 2 | 229 | 1 | 20 | 0 | 0 | 0 | 0 | 3 |
| 28 | 28 | 1 | 227 | 2 | 202 | 0 | 23 | 0 | 0 | 0 | 0 | 10 |
| 29 | 28* | 1 | 141 | 1 | 115 | 0 | 25 | 0 | 0 | 0 | 0 | 8 |
| 30 | 28** | 1 | 44 | 2 | 37 | 0 | 5 | 0 | 0 | 0 | 0 | 3 |
| 31 | 28*** | 1 | 72 | 2 | 55 | 0 | 15 | 0 | 0 | 0 | 0 | 3 |
| 32 | 29 | 4 | 142 | 3 | 98 | 7 | 27 | 0 | 5 | 2 | 0 | 4 |
| 33 | 30 | 4 | 214 | 6 | 136 | 16 | 49 | 0 | 4 | 3 | 0 | 10 |
| 34 | 31 | 4 | 258 | 6 | 179 | 17 | 51 | 0 | 3 | 2 | 0 | 2 |
| 35 | 32 | 4 | 175 | 6 | 105 | 7 | 51 | 0 | 3 | 3 | 0 | 7 |
| 36 | 33 | 5 | 145 | 5 | 97 | 7 | 29 | 0 | 5 | 2 | 0 | 5 |
| 37 | 34 | 3 | 287 | 4 | 211 | 11 | 55 | 0 | 5 | 1 | 0 | 9 |
| 38 | 35 | 4 | 187 | 9 | 144 | 6 | 22 | 0 | 3 | 3 | 0 | 4 |
| 39 | 36 | 3 | 282 | 4 | 211 | 11 | 51 | 0 | 3 | 2 | 0 | 7 |
| 40 | 37 | 3 | 220 | 2 | 178 | 9 | 28 | 0 | 2 | 1 | 0 | 5 |
| 41 | 38 | 5 | 115 | 6 | 52 | 4 | 46 | 0 | 4 | 3 | 0 | 5 |
| 42 | 39 | 6 | 137 | 13 | 80 | 6 | 29 | 0 | 6 | 3 | 0 | 2 |
| 43 | 40 | 4 | 198 | 9 | 149 | 6 | 29 | 0 | 3 | 2 | 0 | 4 |
| 44 | 41 | 4 | 145 | 10 | 80 | 8 | 41 | 0 | 3 | 3 | 0 | 7 |
| 45 | 42 | 3 | 281 | 5 | 239 | 2 | 29 | 0 | 2 | 4 | 0 | 1 |
| 46 | 43 | 4 | 240 | 6 | 149 | 8 | 69 | 0 | 3 | 5 | 0 | 3 |
| 47 | 44 | 3 | 270 | 3 | 175 | 14 | 73 | 0 | 4 | 1 | 0 | 11 |
| 48 | 45 | 3 | 203 | 6 | 149 | 16 | 28 | 0 | 4 | 0 | 0 | 2 |
| 49 | 46 | 6 | 257 | 1 | 225 | 2 | 23 | 0 | 6 | 0 | 0 | 1 |
| 50 | 47 | 7 | 306 | 2 | 203 | 12 | 78 | 1 | 6 | 4 | 0 | 6 |
| 51 | 48 | 4 | 216 | 5 | 123 | 6 | 76 | 0 | 4 | 2 | 0 | 9 |
| 52 | 49 | 6 | 251 | 5 | 149 | 6 | 80 | 1 | 6 | 4 | 0 | 17 |
| 53 | 50 | 7 | 316 | 3 | 220 | 16 | 68 | 0 | 7 | 2 | 0 | 8 |
| 54 | 51 | 8 | 356 | 3 | 159 | 22 | 159 | 0 | 12 | 1 | 0 | 11 |
| 55 | 52 | 8 | 352 | 4 | 136 | 38 | 162 | 0 | 10 | 2 | 0 | 8 |
| 56 | 53 | 4 | 235 | 7 | 126 | 16 | 81 | 0 | 3 | 2 | 0 | 5 |
| 57 | 54 | 4 | 283 | 6 | 119 | 20 | 132 | 0 | 4 | 2 | 0 | 3 |
| 58 | 55 | 5 | 241 | 3 | 108 | 21 | 100 | 0 | 6 | 3 | 0 | 9 |
| 59 | 56 | 3 | 236 | 3 | 122 | 22 | 86 | 0 | 2 | 1 | 0 | 6 |
| 60 | 57 | 5 | 279 | 5 | 178 | 14 | 76 | 0 | 4 | 2 | 0 | 9 |
| 61 | 58 | 8 | 258 | 9 | 115 | 21 | 100 | 0 | 8 | 5 | 0 | 12 |
| 62 | 59 | 10 | 405 | 1 | 163 | 62 | 163 | 0 | 14 | 2 | 0 | 8 |
| 63 | 60 | 8 | 138 | 8 | 78 | 9 | 31 | 1 | 7 | 4 | 0 | 9 |
| 64 | 60* | 1 | 220 | 1 | 182 | 1 | 36 | 0 | 0 | 0 | 0 | 22 |
| 65 | 61 | 2 | 227 | 7 | 167 | 8 | 42 | 0 | 1 | 2 | 0 | 6 |
| 66 | 62 | 3 | 292 | 6 | 186 | 10 | 88 | 0 | 2 | 0 | 0 | 12 |
| 67 | 63 | 1 | 220 | 5 | 90 | 8 | 116 | 0 | 0 | 1 | 0 | 17 |
| 68 | 64 | 2 | 317 | 1 | 170 | 7 | 137 | 0 | 1 | 1 | 0 | 14 |
| 69 | 65 | 3 | 181 | 5 | 134 | 9 | 30 | 0 | 2 | 1 | 0 | 4 |
| 70 | 66 | 4 | 226 | 4 | 168 | 13 | 36 | 0 | 3 | 2 | 0 | 4 |
| 71 | 67 | 3 | 309 | 4 | 227 | 6 | 68 | 0 | 2 | 2 | 0 | 13 |
| 72 | 68 | 3 | 187 | 5 | 137 | 7 | 32 | 0 | 3 | 3 | 0 | 6 |
| 73 | 69 | 4 | 174 | 5 | 93 | 14 | 56 | 0 | 3 | 3 | 0 | 9 |
| 74 | 70 | 2 | 279 | 6 | 137 | 26 | 106 | 0 | 1 | 3 | 0 | 7 |
| 75 | 71 | 5 | 339 | 8 | 202 | 15 | 106 | 0 | 7 | 1 | 0 | 15 |
| 76 | 72 | 4 | 320 | 1 | 216 | 10 | 90 | 0 | 3 | 0 | 0 | 15 |
| 77 | 73 | 5 | 192 | 4 | 107 | 10 | 63 | 0 | 5 | 3 | 0 | 7 |
| 78 | 74 | 10 | 302 | 4 | 132 | 5 | 144 | 0 | 11 | 6 | 0 | 9 |
