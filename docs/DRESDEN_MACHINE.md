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

### C3 — the "luminous path": the ordering exists, the *meaning* does not survive the control
On 60 of 78 pages the brightest-first tour is shorter than ≥95% of random
tours — naively a strong "path" signal. The control kills the reading: the
same test on the four **blank** pages (no glyphs; pseudo-cell grid on bare
plaster) returns rank 0/999 on all four — the *strongest possible* "path"
signal with nothing written on the page. Substrate luminance varies smoothly
across any page (illumination, plaster tone), so *any* brightness ordering of
*any* spatial cells produces short tours. MEASURED, both halves.
**Verdict: the luminance ordering is a real, reproducible measurement; it
carries no evidence of a designed glyph path.** A designed-path claim would
need the inscribed-page effect to *exceed* the blank-substrate effect; here
it does not (blanks saturate the statistic).

### C4 — the photographed column: NEGATIVE (not in this scan set)
Median-centred integer SAD over all 78 scans × 5 template scales: all top-4
hits land on blank pages (mean-SAD 33–34), i.e. low-contrast fits, not
structure. The column's layout (single full-height figure, no register rules)
matches no Dresden section. NEGATIVE, shipped as such. A Madrid Codex origin
is HYPOTHESIS_ACTIVE for the researcher to check against Tro-Cortesianus
scans — it is not a finding of this run.

### C5 — light activation: NOT TESTABLE HERE
A fixed-illumination scan cannot confirm or refute an illumination-dependent
claim. Falsification gate for the future: RTI or multispectral capture of the
physical leaves; pass condition = a glyph-anchored reflectance sequence that
survives the blank-substrate control above; fail condition = the sequence
reproduces on bare plaster. Until such data exists the claim stays
SPECULATIVE.

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
