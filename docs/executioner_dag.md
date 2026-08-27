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
