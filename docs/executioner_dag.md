# executioner_dag.md — CRAM-DF build session (2026-08-19)

Blueprint: "ideate → innovate → design → test → build the complete solution for
forensic digital processing" from the CRAM-DIP packet + manuscript-imaging
research report + CRAM-UNIFIED / Formalization ideation docs.
Environment: Python 3.12.3, numpy 2.4.4, PIL (verified). No prior workspace
manifest — greenfield package; canonical constructs (K-Elimination formula,
star-family inverse rule, adjacency collapse) wired from canon, not rebuilt.

## NODE-S01 — core substrate (DualTrack, KELD, shadow probes, lane comb)
- Type: IMPL  Size: M  Output: cram_df/core.py
- Gate: exhaustive K-Elim over star8/star16 + composite pairs; KELD == floor(L/M);
  fire-sets derived; A8 lane-7 Sqr refusal raises. **Status: PASS**  Float check: PASS

## NODE-S02 — Tower K-Elimination + generalized Sqr-carry (sourced from attached ideation)
- Type: IMPL  Size: S  Output: core.py (tower_k, sqr_carry(p), sqr_carry_fire_set)
- Gate: tower exhaustive over [0, 36·37·73); lane-13 fire set verified 0..255;
  lane-7 refused. **Status: PASS**  Float check: PASS

## NODE-T01 — exact transforms (NTT conv, RCT, ChromaDI, 5/3 lifting)
- Type: IMPL  Size: L  Output: cram_df/transforms.py
- Gate: NTT == unbounded-int oracle (30 random); all round trips bit-exact.
  **Status: PASS**  Float check: PASS

## NODE-T02 — Kill #113 skew witness + INV-8 check lane (sourced from attached ideation)
- Type: IMPL  Size: S  Output: transforms.py (skew_energy_ip, conv2d_modp, check_lane_verify)
- Gate: ⟨I, D I⟩ == 0 on 100 random cases; mod-17 lane agrees with NTT on all runs.
  **Status: PASS**  Float check: PASS

## NODE-U01 — Rational-Grid Exact Unmixing
- Type: IMPL  Size: S  Output: cram_df/unmix.py
- Gate: zero-error recovery at true (p,q); blind grid finds (3,8). **Status: PASS**

## NODE-F01 — forensic probes + provenance ledger
- Type: IMPL  Size: M  Output: cram_df/forensics.py
- Gate: copy-move IoU exact; splice block IoU 20/20 with misaligned mask;
  two-run chain hashes identical; round-trip receipts true. **Status: PASS**

## NODE-D01 — deterministic synthetic evidence
- Type: IMPL  Size: S  Output: cram_df/synth.py — seeded integer generators.
  **Status: PASS**

## NODE-B01 — quarantined classical foils
- Type: IMPL  Size: S  Output: cram_df/baseline_float.py (float BY DESIGN,
  quarantined from lint; PCA error returned as integer milli-MAE). **Status: PASS**

## NODE-L01 — A1 linter
- Type: IMPL  Size: S  Output: cram_df/a1_lint.py — AST scan (float literals,
  true division, float names/attrs), quarantine + self-exempt discipline.
- Gate: verdict PASS on all production files. **Status: PASS**

## NODE-R01 — T1–T9 harness
- Type: TEST  Size: L  Output: run_all.py → RESULTS.md, receipts.json, 8 demo PNGs
- Gate: all checks green. **Status: PASS — 2,582,984 checks, 0 failures**

## NODE-A01 — architecture + opportunity index
- Type: REPORT  Output: ARCHITECTURE.md, CRAM_OPPORTUNITY_REPORT.md. **Status: PASS**

---
## CHECKPOINT — 2026-08-19, all nodes complete
| Node | Status | Output |
|---|---|---|
| S01,S02,T01,T02,U01,F01,D01,B01,L01,R01,A01 | PASS | see above |
Pending: none this session. Phase 2 queued: Rust/NEON port (MANA pattern),
Archimedes Palimpsest real-data run, full Hao–Shi integer RKLT node.
CRAM axiom quick-check: A1 lint PASS; no Garner anywhere (A2 by construction);
no Sqr on lane 7 (refused programmatically); DKAM d=2 < ρ=3 documented;
inverses via extended Euclid only (pow(a,-1,m)), never Fermat.

---
# CAMPAIGN 2 — TARGET-ARTIFACT COMPLETION (opened 2026-08-19)

Plan: /EXECUTION_DAG.md (52 nodes, phases INF/ARC/VES/GPZ/GAL/DRE/SEL/SIN/REP).
Executor: Claude Code against this repo. Definition of 100%: every board closes
as measured-result-at-evidence-size (zero included) or BLOCKED with a Requires:
line naming the researcher-only action. This file remains the append-only
record: node completions and checkpoints land here.

## CHECKPOINT — 2026-08-19 (campaign opened, no nodes executed)

### Completed This Session
| NODE-ID | Status | Output |
|---------|--------|--------|
| (plan authored) | — | /EXECUTION_DAG.md, /CLAUDE.md |

### In Progress
None.

### Pending (dependency order)
INF01 → Track 1 (VES deadline 2026-08-31) ∥ Tracks 2–7 per EXECUTION_DAG.md.

### Files to Deliver
EXECUTION_DAG.md, CLAUDE.md (this commit).
---

## CHECKPOINT — 2026-08-19 (campaign 2, execution session)

### Completed This Session
| NODE-ID | Status | Output |
|---------|--------|--------|
| INF01 | PASS | env verified (py3.12.3/numpy2.4.4/pillow12.1.1); baseline 2,585,391/0 holds |
| INF02 | PASS | cram_dsp/core.py — LANES_8BIT/14BIT/EXT, lane_bound, lanes_for_bitdepth |
| INF04 | PASS | cram_dsp/ingest.py — detect_lattice/seal/unseal, receipted, exactly reversible |
| INF05 | PASS | forensics.Ledger.record_acquisition |
| ARC01 | PASS | 3 windows verified against pinned SHA-256 |
| ARC02 | PASS | docs/ARCHIMEDES_RESULTS.md §2 — 10/15 bands at zero shift; raking-IR margins declared indeterminate |
| ARC04 | PASS | cram_dsp/metrics.py |
| ARC05 | PASS | baseline_float.py — knox_pseudocolor, sharpie_subtract, pca_render (quarantined) |
| ARC06 | PASS | cram_dsp/render.py |
| ARC07 | PASS | docs/ARCHIMEDES_RESULTS.md §5 — head-to-head; Sharpie WINS the lattice axis, recorded |
| ARC09 | PASS (negative) | docs/ARCHIMEDES_RESULTS.md §6 — shipped negative, no undertext claim |
| VES06 | PASS | LICENSE (MIT), NOTICE.md, skills/dsp-analyst/LICENSE |

Run total this session: **75,564,310 exact checks, 0 failures** (analysis/arc_run.py).
Harness baseline unchanged and still green.

### Corrections folded in during the session
- Registration metric v1 compared raw cross-band intensities; DC offset
  dominated and every margin read ~0. Replaced with median-centred integer
  SSD. 10/15 bands then resolved to zero shift.
- Survivability percentages were printing milli-ratios as percents
  (1.000 where 100.000% was meant). Fixed before publication.
- Fingerprint-block statistic does not discriminate on continuous-tone
  sensor data (2048/2048 every path). Null recorded rather than dropped.

### BLOCKED (unchanged)
ARC08 (no XRF assets located on the mirror — Requires: alternative source),
INF09/INF10 (Rust not installed in this container), VES07/GPZ04/SEL02/SIN01
(researcher account or decision actions), DRE01 (scan set provision),
ARC03 (HUMAN-VERIFY gate on annotation fixtures — blocks axis D / NODE-ARC10).

### Next step to resume
NODE-VES01: acquire the Vesuvius ink-label set and run the same
first-contact characterization; Progress Prize deadline 2026-08-31.

## CHECKPOINT — 2026-08-27 (campaign 3: Dresden scan set provided, DRE-01 + glyph machine)

### Completed This Session
| NODE-ID | Status | Output |
|---------|--------|--------|
| DRE01 | PASS | data/dresden/ — WDL 11621 PDF committed + 78 byte-exact page JPEGs, SHA-256 pinned, hash-chained receipts, exact integer per-page characterization; INDEX.md (Förstemann numbering + assumed categories, blank-page positions {29,30,31,64} corroborate the mapping by measurement) |
| (machine) | PASS | cram_dsp/dresden.py — A1-clean glyph machine (integer Otsu, run-based 8-conn components, circular-outward ring signatures, L1 matching, luminance ordering, seeded permutation path test); analysis/dresden_run.py — **636 exact checks, 0 failures**; docs/DRESDEN_MACHINE.md + DRESDEN_MACHINE_RUN.md |

### Measured results (scoped, negatives shipped)
- C2 recurrence: real-cell nearest-code distance median 404 vs 543 random-placement null (Venus pages); dot-form retrieval works; complex-glyph retrieval under-resolved at 684×1350 — limit stated.
- C3 "luminous path": 60/78 inscribed pages give p≤0.05 tours, BUT the blank pages give rank 0/999 with zero glyphs — substrate-luminance autocorrelation explains the effect; no designed-path evidence. Negative shipped.
- C4 photographed column: NOT in this scan set (top-4 template hits are blank pages = null). Madrid Codex origin recorded as HYPOTHESIS_ACTIVE, researcher to check.
- C5 light activation: untestable on fixed-illumination scans; falsification gate defined (RTI/MSI + blank-substrate control).

### Corrections folded in during the session
- otsu_threshold off-by-one: returned last dark bin while ink_mask uses strict <; now returns first bright value; extractor + index regenerated, all cross-checks pass.
- Pre-existing A1 violation in spectral.py:57 (Fraction true-division from campaign-2 commit 40a3344) replaced with exact-reciprocal multiply; pseudoinverse exactness re-witnessed (P@M == D*I); a1_lint back to PASS.

### Gates
G1 outputs at stated paths ✓ · G2 a1_lint PASS ✓ · G3 py_compile clean ✓ · G4 run_all baseline 2,585,391/0 unchanged + dresden_run 636/0 ✓ · G5 DRE01 gate (every page characterized) ✓ · G6 A2/A8/inverse untouched ✓.

### BLOCKED (changes)
DRE01 cleared by researcher file provision. DRE02–DRE05 now PENDING (were BLOCKED on DRE01). All other blockers unchanged from 2026-08-19 checkpoint.

### Next step to resume
NODE-DRE02 (repair-seam map via quant_fingerprint_map) or NODE-DRE04 (KELD strata / tonal windows) on the ingested pages; note scan resolution limit — full-res SLUB captures would lift the C2 complex-glyph bound. Track 1 deadline 2026-08-31 (VES) still governs priorities.

## CHECKPOINT — 2026-08-27 (campaign 3b: discovery sweep — exploratory mode per researcher direction)

### Completed This Session
| NODE-ID | Status | Output |
|---------|--------|--------|
| (discovery machinery) | PASS | cram_dsp/dresden.py extended (4/8-conn labeling, exact hole counting, dot topology census, exact quantile tonal bands, all-pairs L1 matrix); analysis/dresden_discover.py — whole-codex sweep, 9/9 fixture checks; docs/DRESDEN_DISCOVERIES.md catalog; data/dresden/derived/ galleries (paths/dots/bands for all 78 pages) |

### What the sweep surfaced (MEASURED, exploratory ranking)
- D1: 7,834 cells all-pairs matched; 35 recurrence clusters (size>=4) at data-derived threshold L1<=177; 12 exact cross-page code identities (L1=0); numeral-dot form clusters span black AND red instances (code reads form, not pigment); serpent-body segment cluster spans p39/p44/p61/p65/p70.
- D3: 119 large-figure regions auto-detected; 2,124 interior-element->glyph code matches catalogued (the "dressing" claim now has a machine-generated candidate list, best L1 287).
- D4: 10,685 hollow vs 23,725 solid dots codex-wide by exact topology; densest hollow-dot pages p72, p71, p47, p48, p41 (candidate preparation/stitching loci for the researcher's shell claim).
- D2/D5: per-page path overlays + tonal-band structure maps for every page (no page passed silently); D6 opportunity index has one row per page.

### Direction note
Researcher redirected from refutation framing to discovery framing: the machinery must surface instances itself rather than test single examples. DRESDEN_MACHINE.md verdicts stand (substrate caveat restated once in the catalog); the catalogs are the exploration surface.

### Gates
run_all 2,585,391/0 unchanged · dresden_run 636/0 · discover 9/0 · a1_lint PASS · py_compile clean.

### Next step to resume
Deep-dive the top D1 clusters and D3 pairs at their coordinates; DRE-02 (seams) / DRE-04 (KELD strata) remain PENDING; full-res SLUB captures would lift the code resolution bound.

## CORRECTION — 2026-08-27 (C4 false negative reversed; localizer rebuilt)

Researcher challenged the C4 NEGATIVE (photographed column "not in this scan
set") and was right: the column is **scan 73 = Förstemann page 69**, right
column, (64, 768)–(≈274, 1350). Root cause of the false negative: median-
centred luma SAD is not discriminative across scan generations (blank pages
win as low-contrast fits). Fix shipped: integer edge-orientation matching —
`dresden.orientation_planes` (octant binning, no trig), `pool_planes`,
`cooccurrence_map` (exact int64 einsum), `locate` (mirror-aware via exact
bin permutation gx→−gx ⇒ k↔k^2). `analysis/dresden_locate.py`: 6/6 checks;
winner margin 222 milli over best other-page placement; panels
`demo/dresden_located_p69.png` / `_page.png`. DRESDEN_MACHINE.md §C4
rewritten; Madrid hypothesis withdrawn. Machine-surfaced: p65 column is the
structural twin of the p69 column (second-best placement, same in-page
coordinates). Lesson folded into the module docstring: match structure, not
brightness, across scan generations.

## NODE (white machinery) — 2026-08-27

White-gradient machinery built per researcher direction (the illustrated
pipeline, previously absent): dresden.order_stat / highlight_freeze /
white_nodes / white_path(min_sep) — all exact. analysis/dresden_white.py:
7/7 checks; worked example on the located p69 column
(demo/dresden_white_p69.png: original | frozen | numbered white path);
freeze + white-path overlays for all 78 pages in data/dresden/derived/white/;
catalog docs/DRESDEN_WHITE.md; receipts data/dresden/white_receipts.json.
DRESDEN_MACHINE.md C3 reframed: white-node sequences are the exploration
surface; glyph-median path test demoted to appendix; blank-substrate control
retained as constraint on design claims.

## NODE-DRE02 + NODE-DRE04 — 2026-08-27

DRE02 PASS: analysis/dresden_seams.py (4/4 checks). P1 requantization
fingerprint: NULL on all 78 continuous-tone scans (0 flagged blocks) —
same null as the Archimedes sensor data, recorded. P2 block-median
discontinuity: per-page candidates enumerated (990-milli threshold, floor
24), panels for the six highest-candidate pages in derived/seams/.
docs/DRESDEN_SEAMS.md.

DRE04 PASS: analysis/dresden_strata.py (3/3 checks). KELD strata (STAR8,
band = floor(L/36) from the residue pair) rendered for all 78 pages
(derived/strata/); pale-field ranking puts scan24/p24 (Venus preface) as
the palest INSCRIBED page, above two actual blanks; tonal windows over the
six palest pages rendered — coherent bright-plaster zones are the
latent-content candidates for multispectral follow-up. docs/DRESDEN_STRATA.md.

## NODE (pigment lens + exhibit localization + exactness fix) — 2026-08-27

Researcher exhibits (WDL screenshot with blue column/spear-bearer; manual
SHADOWS adjustment) both localized mechanically to **scan 73 = p69** — the
same page as their photographed column; margins +518/+587 milli. First
attempt mis-localized exhibit A to p49 off a loose crop + short scale
range; caught by the mandatory visual verification and corrected —
verify-then-accept is now stated in the run. New machinery:
dresden.pigment_classes (exact 4-way substrate/black/red/blue partition by
stated integer margins) + shadow lens (freeze window 30..500 milli, the
machine version of the researcher's shadows slider); renders for all 78
pages (derived/pigment/), blue-region catalog (largest blue regions incl.
the p69 blue column), docs/DRESDEN_PIGMENT.md, receipts.

Exactness fix folded in: sector octants re-based to axis-centred bins and
ring/sector codes moved to the EXACT rational centroid (offsets scaled by
ink count — floor-divided centroids break mirror symmetry). Dihedral
invariance now exact on asymmetric fixtures (mirror/rot90/rot180 = 0).
dresden_run 636/0; discover 9/0 (21 ring-code clusters at threshold 205);
pigment 6/6.

## NODE (white-trail machinery + form vocabulary final) — 2026-08-27

Researcher clarified the idea: continuous WHITE TRAILS (gradient-to-white
filaments), not brightness-ranked blobs; and the machine should NAME the
best pages for each experiment. Built:
- dresden.local_bright_field (luma minus block SUBSTRATE median — plain
  medians read ink-dense blocks wrong; caught and fixed),
  filament_components (elongated locally-bright components with white
  cores), trail_polyline, trail_glyph_sequence.
- analysis/dresden_trails.py 10/10: trail overlays for all 78 pages
  (derived/trails/); machine ranking of best trail pages = p70, p51, p37,
  p52, **p73** (the page the researcher pointed at — independent
  convergence), p36; per-page glyph sequences along the glyph-richest
  ascending trail with numbered overlays + sequence strips (demo/);
  dressing-experiment page ranking. Blank pages rank trail-rich —
  shipped as measurement (trails are substrate phenomena).
- Form vocabulary final (dresden_vocab 7/7): rule-chosen threshold 1410
  (largest with max family <= 500); 15 families, dot family 496, full
  contact sheets derived/clusters/.

## RULES CHANGE — 2026-08-27 (researcher directive: exploration rules)

docs/RULES_OF_EXPLORATION.md installed and made binding via CLAUDE.md:
(1) no hypothesis closure while machinery is under construction — results
are MEASURED / METHOD-LIMITED / OPEN only; no "closed avenues" anywhere;
(2) controls must not presuppose the hypothesis false — the blank-page
control's null model (blanks = no signal) is rejected by the researcher's
hypothesis (continuous strip; flat white = base state), so its prior
"no designed path" reading is WITHDRAWN as a verdict (measurements stand);
(3) failed methods preserved as receipts (C4 chain is the template);
(4) evidence vs visualization split — matchers run on evidence transforms
only; (5) localization control battery required; (6) sequences require
multi-path agreement; (7) morphology before semantics. Existing docs
reframed accordingly (this record, per its append-only rule, is not
rewritten — this entry IS the record of the change).

## R1–R4 — 2026-08-28 (production spec implemented; fork material integrated)

Researcher's production specification implemented in full, plus integration
of the ARCHIMEDES suite the researcher supplied:

* midrank_normalize — imported from BRANCH_SWEEP.md B2/B6, where independent
  contrast stretches were shown to drive and even INVERT a metric. Both sides
  of every cross-generation match are now marginal-equalized.
* decide_with_abstention — archnet void rejection: thin margins decline to
  name a winner. The no-closure rule enforced in code.
* Branch-exhaustion posture: all controls run and are reported before any
  statement, none used to close anything.

R1 localizer (6/6): weighted orientation planes (edge confidence), anisotropic
scale sweep, exact integer COSINE scoring, full control battery. TWO of my own
failures were caught by the battery and are kept as receipts: (a) raw
co-occurrence scores were not comparable across templates — texture floor
2380 above the real query 826; (b) the first battery compared a different
template's best score to the query's, which is meaningless — replaced by the
per-query null (winner 826, median 685, min 648, best blank-page 709, rank
percentile 1000/1000).

R2 white-field v2 (7/7): node evidence records (contrast, gradient
magnitude/direction, chroma spread, combined score — a warm bright mark can
no longer outscore a neutral one); three independent orderings with exact
pairwise agreement; written-zone vs bare-substrate comparison (written zones
carry HIGHER node contrast on every page where both exist — 18/13, 16/12,
29/12, 21/19); cross-page facing-edge trail continuity: 96 alignments, null
not yet computed and flagged as such.

R3 radial decomposition: character centre -> 4 rings x 8 sectors read
outward, 31 pieces on the p69 character matched codex-wide with DIRECT /
ROTATED / MIRRORED / ROT+MIR reported separately and the 1:3:1:3 chance
baseline stated (observed 4/14/3/10 sits at baseline).

R4 dot morphology (6/6): 34,410 round marks measured with no semantic
labels; open marks are a larger/thicker population (median area 98 vs 39,
thickness 1510 vs 1000, 325/1000 overlap with the filled IQR); spacing
regularity per page and class; recurrence ranking against the located p69
column (nearest: p58, p70, p69, p63, p62).

docs/DRESDEN_MACHINE_STATUS.md added: per-stage VALIDATED /
BUILT-UNVALIDATED / NOT-BUILT, and the four nulls that must exist before the
trail hypothesis can be leaned on. Nothing is closed.

## SCALES S1/S2 — 2026-08-28 (framing corrected by the researcher)

Researcher correction: "We're in exploration there won't be any lean." The
status document had framed the outstanding nulls as gates that would let
exploration lean on a hypothesis. Wrong frame — exploration does not
accumulate toward a ruling and there is no verdict horizon. Nulls reframed
throughout as SCALES: instruments that attach a unit to a reading, gating
nothing. Status vocabulary changed from BUILT/UNVALIDATED to BUILT, NO SCALE
YET.

analysis/dresden_scales.py (4/4):
* S1 path-agreement scale — three orderings over the same nodes vs 15 seeded
  shuffles that permute node POSITIONS while keeping every attribute exact.
  70 of 78 pages sit inside the shuffled range; 8 sit above every shuffle
  (p14, p19, p28*, p29, p51, p52, p59, p74).
* S2 continuity scale — consecutive scan pairs: 96 alignments over 77 pairs
  (1246 per 1000 pairs, 40/77 pairs align). Non-adjacent seeded sample:
  162 over 200 pairs (810 per 1000, 75/200 align).

Both readings ship with their unit and nothing is concluded from either.
Remaining unbuilt instruments: trail-vs-materials discrimination (needs
physical-object or multi-illumination evidence) and higher-resolution
capture (the 684x1350 bound on every matching number).

## SEGMENTATION — 2026-08-28 (a dropped deliverable, recovered)

Researcher instruction: "go back to the beginning of our session and read it
again." Turn one asked for the codex saved to the repo "with each page
**carefully segmented** numbered and grouped into common assumed categories."
Three verbs. Only two were built: `data/dresden/INDEX.md` numbered the pages
and grouped them into sections, and the task was written down as "pages
numbered + grouped into assumed categories" and marked complete. The
segmentation was silently dropped, and every later stage stood on its
absence — figure detectors that merged a page into one blob, glyph detectors
returning three boxes for a column holding a dozen glyphs.

analysis/dresden_segment.py — 78 pages, **17,552 numbered elements**,
hierarchy `leaf -> registers -> zones -> rows -> cells`, 8 geometric
categories. New production primitive `cram_dsp.dresden.open_line`: exact
integer morphological opening by a straight line, via prefix sums.

Totals: 376 figure, 11,679 glyph_block, 878 numeral_bar, 4,205 numeral_dot,
4 panel_ground, 273 rule_h, 137 rule_v, 0 margin.

Four defects found by this stage, each kept as a receipt:

1. Every geometric threshold was keyed to the SCAN FRAME. Each WDL scan
   carries slivers of the ADJACENT LEAVES, so the frame is ~20% wider than
   the page and its edges are the neighbours — "40 px from the edge" was
   measuring the next leaf. `leaf_block` locates the gutter and mount bands
   as dark-fraction peaks in the outer quarter (rows: outer fifth).
2. Register rules detected by component SHAPE returned ZERO on scan 50,
   whose rules are plainly visible: a rule touches the red-brown mottling of
   the damaged plaster and the component becomes a blob. Replaced by a line
   opening, which tests the property a rule actually has.
3. A single gap threshold per zone under-splits dense writing. Cells wider
   or taller than 3/2 of the page's own median glyph cell are re-cut at the
   minimum of their own projection.
4. Red bar-and-dot numerals were invisible to a black-ink-only cell pass;
   folding red into the same projection merged them into their neighbouring
   glyph cells. They get their own component pass.

MEASURED limits, nothing closed:
* Line-drawn figures are not separable from dense line-drawn writing at
  684x1350. Figures carry their provenance (`colour_mass` reliable,
  `stroke_mass` candidate). The discriminator tried — largest undilated
  stroke as a share of the mass — does not separate them: 52/1000 on 402
  raw strokes for the true seated figure of p69 (scan 73) against 43/1000
  on 399 for a block of merged writing on the same page. Both numbers ship
  with every stroke-mass figure for a higher-resolution capture to test.
* `margin` fired 0 times across all 78 pages; the category is subsumed by
  the leaf boundary. Reported as zero, not removed.

The p69 seated figure — the column this whole build exists to read — is now
found by the machine itself (scan 73, element 98) instead of by being
pointed at.

Gates: FIXTURES 18 checks / 0 failures; a1_lint PASS; py_compile clean;
run_all 2,585,391 checks / 0 failures.

Next: re-run the downstream machinery (correspondence experiment, the
8-panel sheet) on this segmentation substrate rather than on ad-hoc
per-stage detectors.

## p17 CORRESPONDENCE — 2026-08-28 (researcher-selected page)

Researcher: "Do page 17 of 78 — I definitely see this page." Scan 17 is the
concept illustration's layout made literal: the oval icons float in the SAME
OPEN FIELD as the figures, not in a text grid as on p47 and p69.

New production primitive `cram_dsp.dresden.local_dark_field` — per-pixel
darkness below the LOCAL substrate level (lower-quartile luma of each 24x24
block's non-ink pixels). An evidence transform, not an enhancement. It exists
because global Otsu misses this page's figures entirely: under the previous
detector all five "figures" on p17 were blocks of WRITING and not one of the
four real figures was found.

Four separations tried, all receipted: second global Otsu (selects 323/1000
of the page, shading included); removing heavy ink (destroys the figures —
the line is not lighter than the cut); stroke-width opening (separates figure
from writing but not figure from icon — the ovals are thin rings too); and
cutting the segmentation cells out of the targets (shreds the figures, since
the cell pass also boxes figure parts). What works is TOPOLOGY: an oval is a
small CLOSED loop, the figure line is a large open structure. 67 icons
(median 34x41, all carrying a hole) against 10 targets, disjoint by component
identity.

Two defects this run found in its own machinery:
* SELF-MATCHING. With targets taken as thin-stroke components the ovals
  joined the figure's component, so every target contained the icons around
  it. That run's top result (icon 32 -> T5, IoU 547, boundary overlap
  982/1000) is visibly the icon landing on a NEIGHBOURING OVAL outside the
  figure. Caught by looking at the picture, not by a score.
* DEGENERATE NULL. "608 of 608 clear their own matched null" is near
  tautological — the argmax of a distribution beats its own p99. Replaced by
  a FOREIGN-ICON control: icons from scan 5, same extraction rule, same
  targets.

MEASURED, natural scale (the researcher's specification — original size
before resizing): p17's own icons median IoU 389 / p75 455 / p95 577 /
max 684 (n=670); foreign icons from scan 5 median 391 / p75 473 / p95 574 /
max 696 (n=400). 30 of 670 exceed their target's foreign p95 against ~34 by
chance — at or below chance. 0 pass the topology gate. Icon preference tracks
target AREA (the largest target, a writing block, takes 17 of 67).

On the permissive scale ladder: 407 vs 412 median, 68 over foreign p95, 3
pass topology — and every one of the top eight chose scale 2/3 or 3/4, the
shrinkage bias already receipted on p47.

Visual verification: the best natural-scale fit on a figure (icon 3 -> T3,
IoU 684, boundary overlap 966/1000) is a contour arc lying along the
figure's hem line. High score, no correspondence.

METHOD-LIMITED: local window IoU on a sparse line drawing is dominated by
local INK DENSITY, not shape, so any ~35 px form scores ~400/1000 wherever
density is comparable. The objective has almost no shape selectivity at
684x1350 and cannot yet address the correspondence question. This is a
statement about the objective function, NOT about the researcher's
hypothesis, and it closes nothing.

Gap stated: three of four figures are targets; the top-left figure
(scan y180-441 x71-245) did not clear the size floor.

Next instrument (a scale, not a gate): an edge-orientation agreement score
inside inked windows; density normalisation; higher-resolution capture.

Gates: FIXTURES 18/0, a1_lint PASS, py_compile clean, run_all 2,585,391
checks / 0 failures.

## HIRES — 2026-08-28 (the resolution bound, removed)

Researcher, twice: "When I zoom into this image it's visually obscured and
lower quality than what I gave you — is this what you're using or what you're
showing me?" Answer, established by inspecting the source: BOTH. The
researcher's PDF embeds 78 images at 684x1350; that is its native resolution
and nothing here downsampled it. The blur is in the source file.

Every matching number this campaign has produced carried "the 684x1350
resolution bound" as a named limit (DRESDEN_MACHINE_STATUS.md instrument 4;
DRESDEN_P17.md section 6). The bound was never intrinsic — it was an artifact
of the delivery format.

tools/fetch_slub.py — Codex Dresdensis, Mscr.Dresd.R.310, Saechsische
Landesbibliothek Dresden (SLUB), Public Domain Mark 1.0 as declared in the
object's own METS record, reached through the SLUB OAI-PMH endpoint.
78 pages at **3874x7649**: 5.7x linear, **32x the pixels**.

Page correspondence is VERIFIED, not assumed: each fetched page is downscaled
to the PDF page's size and correlated against it. Identity correlation min
990 / median 992 / max 996 per 1000 across all 78; zero failures. Receipts
(URL, byte length, SHA-256, dimensions, correlation) in
data/dresden/hires/RECEIPTS.json, digests pinned in SHA256SUMS.txt. The 386 MB
of images stay out of git and are regenerable by re-running the tool.

What this changes, visibly: at 684 the interior structure of a glyph icon is
not resolved at all. At 3874 it is. DRESDEN_P17.md concluded METHOD-LIMITED —
"local window IoU on a sparse line drawing is dominated by ink density, not
shape ... almost no shape selectivity at 684x1350". That conclusion stands as
written for that resolution, and the likeliest reading is now that the
objective had no internal structure to work with rather than that the
objective is wrong. Both readings stay open; nothing is closed.

RESEARCHER REFRAMING, recorded: "the ones with the dots are the turtle shell
at different angles ... these are not going to be in a character." The dotted
ovals are one object depicted at different viewing angles, not components
that assemble into the figure. The icon-to-character registration test is
therefore the WRONG TEST for this population, and is not to be re-run on
them. The right test is a POSE-FAMILY test: if these are one object rotated,
the interior dot count and arrangement stay stable while the outline
compresses along a foreshortening axis; if they are distinct signs, the two
vary independently. Measurable exactly, and now resolvable.

demo/dresden_p17_dotted_icons.jpg — all 52 icons on p17 carrying interior
dots (of 67), cut from the SLUB original and legibly numbered, so the
researcher can point at specific glyphs. Open question put to the researcher:
their "zone 122 is a face" and "162 I've seen on other pages" do not match
this repo's segmentation IDs (122 is a numeral bar over blank plaster, 162 a
fragment of line over the red rule), so the numbering they are reading is not
identified yet.

## HIRES RENDER — 2026-08-28 (the second half of the researcher's complaint)

Researcher, a third time: "The quality the images that you're showing me are
those what you're looking at because those are way lower quality than what I
gave you."

Two separate facts, and only one was answered before.

FACT 1, now verified rigorously rather than by byte-scan. A full walk of the
PDF's 491 indirect objects finds 156 image objects, of which exactly 78 are
page images at 684x1350 DCTDecode. Total image content: 72.0 M pixels =
78 x 684 x 1350 exactly. There is nothing else in that file. The source was
not degraded here; it simply contains no more detail.

FACT 2, and this one was the agent's fault. The analysis ran on those 684
pages AND the delivered overlays were drawn on them too, upscaled 2x, at JPEG
quality 66-78 — and the per-registration overlays used 6x NEAREST. The
pictures handed back were therefore worse than even the 684 source allowed,
and the researcher could not read their own codex in them.

Fixed: analysis/dresden_segment.py and analysis/dresden_p17.py now draw every
overlay on the SLUB scan (1700 px wide render, from 3874x7649) whenever it is
present, falling back to the PDF page when it is not. Element boxes are the
same exact integers in scan coordinates; only the surface they are drawn on
changes, and it is the library's own scan of the same object with identity
verified per page.

All 78 segmentation overlays and the p17 inventory regenerated. Counts
unchanged and reproduced exactly: 17,552 elements, 376 figure, 11,679
glyph_block, 878 numeral_bar, 4,205 numeral_dot, 4 panel_ground, 273 rule_h,
137 rule_v, 0 margin. FIXTURES 18/0, a1_lint PASS.

Still to do: re-run the ANALYSIS natively at high resolution (thresholds and
size windows scale by 5.66), not merely the rendering. The measurements above
are still 684-derived.

## RECURRENCE — 2026-08-28 (researcher-selected glyph; the method fails its control)

Researcher: "162 is on this page see it the face", and earlier "162 I've seen
on other pages." Resolved a numbering mismatch first — their 162 is on PAGE 7,
not p17 (p17's element 162 is a figure's foot). p7 element 162 is a 173x102
block this repo's detector merged into one `figure` (the stroke_mass merging
defect), and inside it cartouche c2 is a face in profile within a dotted oval:
eye, snout, jaw, legible at high resolution only. At 684 the glyph is 63x31 px
with no resolved interior, which is why it was invisible to both of us.

analysis/dresden_recur.py searched all 78 pages at 1937 px working width from
the SLUB scans, 8 dihedral poses, weighted orientation planes, midrank
normalization, exact integer cosine.

Control battery: positive control passes (self-match 747, rank 1 of 78). Best
other page scan 19 / p19 at 721. Median 702, min 667, spread 80.
BEST NEAR-BLANK PAGE 712 — and scans 29 and 31, which are bare plaster, rank
6th and 7th of 78, above 71 pages carrying writing. The best genuine page sits
just 9 points above blank plaster on an 80-point scale.

METHOD-LIMITED. A pooled orientation-histogram cosine compares the texture
statistics of a sliding window; on a codex where nearly every window is dense
line-work of similar stroke density, those statistics are near-constant. This
is the TEXTURE FLOOR already receipted in DRESDEN_MACHINE_STATUS.md for the
localizer — used again here and failing the same way. Recorded as an agent
error, not a property of the codex.

NO CLAIM is made about whether the glyph recurs. The researcher's recurrence
claim stays OPEN and is not contradicted by anything measured here.

Surfaced as candidates for the researcher's eye only, carrying no score-based
support: scan 8 / p8 (an oval cartouche with an internal profile head, closest
by eye) and scan 19 / p19.

Next instrument: cartouche-to-cartouche shape comparison against the 11,679
glyph_block cells already segmented across 78 pages — ring/sector signature,
dihedral-normalized, plus interior topology. Page texture cannot enter such a
comparison because blank plaster yields no cartouche at all. Feasible only now
that cartouche interiors are resolved.
