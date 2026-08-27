# The glyph machine — what the illustrations claim, what the codex measures

NODE-DRE01 + the machine build. Companion files: `docs/DRESDEN_MACHINE_RUN.md`
(full run transcript with every number), `data/dresden/INDEX.md` (page index),
`data/dresden/receipts.json` / `machine_receipts.json` / `queries/receipts.json`
(hash-chained provenance).

The researcher supplied two concept illustrations and a photographed codex
column (pinned as exact decimations in `data/dresden/queries/`), and asked for
the machine that *legitimately* does what the illustrations suggest — with the
explicit acknowledgment that the illustrations themselves are not accurate.
This document decomposes the illustrations into testable claims, describes the
machine, and reports what the actual scan set measures. Evidence-class labels
follow the archeoastronomy-codex working standard.

## 1. Claim decomposition

| # | Illustrated claim | Testable on this scan set? |
|---|---|---|
| C1 | Glyphs can be segmented; each has a distinctive internal structure ("code") read circularly outward from its center | Yes |
| C2 | The same code recurs elsewhere on the page and on other pages ("dressing the figure") | Yes |
| C3 | A luminance ordering over the glyphs traces a coherent, non-random path (the "luminous path", 1→12) | Yes — with a control |
| C4 | The photographed column belongs to this codex | Yes (localization search) |
| C5 | The path is "activated by light" (eclipse-phase illumination) | **No** — a single fixed-illumination RGB scan cannot test an illumination-dependent claim. Testing C5 requires multi-illumination captures (RTI/MSI) of the physical object. Stated, not simulated. |

## 2. The machine (named transforms, fixed parameters, exact integers)

`cram_dsp/dresden.py`, A1-clean (zero float, statically linted). Every value
is an exact integer function of the scan bytes; nothing is generated,
inpainted, or enhanced. Renders are display-seam only, nearest-neighbour.

| Stage | Transform | Parameters |
|---|---|---|
| Luma | `(77R + 150G + 29B) >> 8` | weights sum to 256 |
| Ink threshold | integer Otsu, cross-multiplied variance comparison (no division evaluated) | per page |
| Segmentation | run-based two-pass connected components, 8-connectivity, union-find | after 2-step shift-OR dilation |
| Glyph cells | component bounding boxes | area window [120, 12000] px |
| Glyph code | milli ink-fraction per concentric ring about the ink centroid; radii by exact integer sqrt (table search); scale-normalized | 12 rings — this is the literal, honest version of "searched circularly outward from center" |
| Matching | exact L1 distance between ring signatures, ranked, ties preserved | — |
| Luminance order | cells ranked by exact lower-median interior luma | — |
| Path test | L1 tour length of that ordering vs 999 seeded Fisher–Yates permutations (deterministic LCG); exact p-value numerator | seed 20260827 |

Self-tests: 20+ exact fixture checks (component counts/areas, dilation areas,
ring-signature invariance under 90° rotations, LCG determinism, known tour
lengths). Full run: **636 exact checks, 0 failures**.

## 3. Ingestion (DRE-01) — the codex is now in the repo

- Source: WDL item 11621 (SLUB Mscr.Dresd.R.310), researcher-provided PDF,
  SHA-256 `239de6327eff…` pinned; committed at
  `data/dresden/source/wdl11621_codex_dresdensis.pdf`.
- 78 embedded JPEGs extracted **byte-exact** (raw DCTDecode streams, no
  re-encode) to `data/dresden/pages/`, each pinned in `SHA256SUMS.txt`,
  each acquisition and decode receipted (`receipts.json`, hash-chained).
- Per-page characterization (dimensions, luma extrema/median, integer-Otsu
  threshold, ink coverage in milli) in `characterization.json` — the gate
  "every page characterized before analysis" is met.
- Numbering: scans 1–78 (OBSERVED) mapped to Förstemann pages 1–74 + four
  unnumbered blanks (EPIGRAPHIC assumption) — **corroborated by measurement**:
  the four predicted blank positions (28\*, 28\*\*, 28\*\*\*, 60\*) are
  exactly scans {29, 30, 31, 64}, the four near-blank scans by ink coverage
  (MEASURED). Categories in `INDEX.md` are the commonly assumed groupings
  (SLUB content description / Thompson tradition) and are labeled as
  consensus, not measurement.

## 4. Results

### C1 — segmentation and per-glyph codes: WORKS, with a resolution limit
7,834 glyph cells across the codex; every cell carries a 12-ring integer
code. MEASURED. At this scan resolution (684×1350 per page; a glyph block is
roughly 20 px) the code is under-resolved for complex glyph interiors — the
stated remedy is the full-resolution SLUB capture, not a cleverer code.

### C2 — recurrence: REAL for simple forms, structural, resolution-bounded
Query page Förstemann 46 (first Venus page, 140 cells) against pages 47–50
(373 cells): median nearest-neighbour code distance **404** milli-L1 for real
cells vs **543** for a seeded random-placement null on the same pages — real
cells match better than chance placement (MEASURED). The best cross-page
retrievals are genuine same-form pairs (numeral dots retrieve numeral dots,
L1 = 104, 138; see `demo/dresden_match_panel.png`). Complex glyph retrieval
is not demonstrated at this resolution — reported as a limit, not claimed.

### C3 — the "luminous path": OPEN — machinery under construction (see `docs/DRESDEN_WHITE.md`, `docs/DRESDEN_TRAILS.md`)
**Status per `docs/RULES_OF_EXPLORATION.md`.** The white-node and white-trail
pipelines are the CURRENT operationalizations of the researcher's illustrated
hypothesis — implementations of the hypothesis, not adjudications of it.
Sequences, trails and their statistics are MEASURED; what they encode is the
researcher's to interpret once the machinery is validated.

On the blank-page control below: the researcher has identified its hidden
assumption — under the hypothesis the codex is a continuous strip, trails may
run THROUGH page boundaries, and flat white is the BASE STATE of the effect,
so blank pages carrying bright structure is consistent with the hypothesis,
not a null against it. The control's numbers stand as measurements; the
"no designed path" reading previously drawn from them is WITHDRAWN as a
verdict and the question is OPEN.

#### Appendix (failed-control receipt): the original glyph-median path test
On 60 of 78 pages the brightest-first tour is shorter than ≥95% of random
tours — naively a strong "path" signal. The control kills the reading: the
same test on the four **blank** pages (no glyphs; pseudo-cell grid on bare
plaster) returns rank 0/999 on all four — the *strongest possible* "path"
signal with nothing written on the page. Substrate luminance varies smoothly
across any page (illumination, plaster tone), so *any* brightness ordering of
*any* spatial cells produces short tours. MEASURED, both halves.
Recorded reading at the time: the ordering carries no evidence of a designed
path. Per the exploration rules this verdict is WITHDRAWN — the control's
null model (blanks = no signal) is rejected by the hypothesis itself
(continuous strip; flat white as base state). The measurements stand; the
question is OPEN pending validated machinery.

### C4 — the photographed column: **FOUND — scan 73, Förstemann page 69, at (64, 768)**

Failed-method receipt (permanent, per `docs/RULES_OF_EXPLORATION.md` rule 3):

```
Previous method:    median-centred luma SAD, 1/8 scale
Result:             FALSE NEGATIVE ("not in this scan set")
Failure mechanism:  insufficient invariance to scan generation, colour
                    grading, illumination, and contrast — blank pages win
                    as low-contrast fits
Replacement:        integer edge-orientation localizer (octant planes,
                    pooled exact co-occurrence, mirror-aware)
Confirmed:          scan 73 / Förstemann p69 / x 64–274 / y 772–1350
Verification:       independent stroke-for-stroke visual comparison
                    + numerical margin (222 milli over best other page)
```

**Correction.** The first run shipped a NEGATIVE here. The researcher
challenged it, and the researcher was right: the column is on **page 69**
(rainy-season/serpent section), right-hand column, full-res coordinates
(64, 768)–(≈274, 1350). Verified two ways: stroke-for-stroke visual match
(`demo/dresden_located_p69.png`) and the fixed matcher below
(milli-score 9434 vs 7720 for the best other-page placement — a 222-milli
margin; `analysis/dresden_locate.py`, 6/6 checks).

Why the first matcher failed, on the record: median-centred luma SAD does
not survive a change of scan generation — the photograph's colour grade
differs from the WDL scan, brightness statistics decorrelate, and blank
pages win as low-contrast fits. Ink **structure** survives re-photography;
brightness does not. The production localizer now matches quantized
gradient orientations (`orientation_planes` — integer octant binning, no
trig; `locate` — pooled exact co-occurrence, mirror-aware with the exact
bin permutation). The Madrid hypothesis from the first run is withdrawn.

Machine-surfaced bonus: the second-best placement overall is **page 65** at
nearly the same in-page coordinates — the p65 and p69 columns share their
composition (same section, same layout), which the matcher sees
structurally. MEASURED; interpretation open.

### C5 — light activation: METHOD-LIMITED (OPEN)
A fixed-illumination scan cannot confirm or refute an illumination-dependent
claim — the limit is in the data, not the hypothesis. Future instrument: RTI
or multispectral capture of the physical leaves, with controls whose null
model the researcher agrees to in advance. Until then: OPEN.

## 5. Scope statement

Where this overlaps existing practice: glyph segmentation and template
retrieval on Maya codices exist in the literature as float pipelines. The
differentiation axis here is exactness: every statistic is an integer with a
hash-chained receipt, the permutation null is deterministic, and the whole
run is bit-reproducible (`python3 analysis/dresden_run.py`). No accuracy
claim against incumbent glyph-retrieval systems is made — none was measured.

## 6. Reproduce

```bash
python3 tools/extract_dresden.py        # re-extract + characterize (idempotent)
python3 tools/build_dresden_index.py    # regenerate INDEX.md (gated)
python3 analysis/dresden_run.py         # machine self-tests + full run
```
