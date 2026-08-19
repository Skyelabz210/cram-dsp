# EXECUTION_DAG — Target-Artifact Campaign (all boards to 100%)

Blueprint source: `BOUNTIES.md` + `BENCHMARKS.md` §2 (the external scoreboard).
Executor: Claude Code, against this repo (`Skyelabz210/cram-dsp`).
Session record: append node completions and checkpoints to
`docs/executioner_dag.md` — never overwrite it. This file is the plan; that file
is the record.

**Definition of 100%:** every board closes in exactly one of two states —
(a) a measured result at the size the evidence supports, **including zero**, or
(b) BLOCKED with a `Requires:` line naming the one thing only the researcher can
do (account, form, licence, outreach, file provision). No node may end ambiguous.
Negative results ship (`BENCHMARKS.md` §3 rule 3).

---

## INVARIANTS (check before every node)

```
I1  ZERO FLOAT on production paths. Foils live in baseline_float.py only
    (quarantined by name in a1_lint). If a node needs float, STOP and flag.
I2  MANIFEST FIRST. Read MANIFEST.md and `git ls-files` before writing anything.
I3  GATE BEFORE ADVANCE. "Runs" is not done. Gate checklist passed is done.
I4  CLEAN STOP. Approaching context limit: checkpoint to docs/executioner_dag.md,
    present completed files, stop.
I5  MARKDOWN OUT for documents; .py/.rs for code.
I6  NO REDUNDANCY. cram_dsp already holds K-Elim, KELD, lane comb, NTT, 5/3,
    RCT, ChromaDI, unmixing, ledger, fingerprints, copy-move, A1 lint,
    fetch_tiff. Wire to them. SKIP-EXISTS anything already on disk.

CRAM axioms: A1 zero float · A2 no Garner / no mixed-radix / no positional
decode — magnitude by K-Elimination only · A3 lane ops are homomorphisms (Γ=1);
Sqr is a read-only probe on lanes 11/13 · A8 NO Sqr on lane 7, refuse don't warn
· DKAM ρ=3 > d=2 · inverses via pow(a,-1,m) (extended Euclid), NEVER
pow(a,m-2,m).

Gate checklist per node:
G1 outputs exist at stated paths · G2 zero-float grep + a1_lint PASS ·
G3 python3 -m py_compile (or cargo check) clean · G4 tests pass ·
G5 node-specific gate met · G6 axiom quick-check (A2/A8/inverse guard).

Reporting rule (binding): where a measurement overlaps an existing method,
report it fully scoped — axis, exact conditions, where the differentiation
lives — never a bare verdict.
```

## PARALLEL TRACKS & CRITICAL PATH

```
Track 1 (DEADLINE 2026-08-31, Progress Prize):
  INF-01 → INF-05 → INF-06 → VES-01 → VES-03 → VES-05 → [VES-06, VES-07 HUMAN]
Track 2 (Archimedes, no deadline): INF-02..04 → ARC-01..10
Track 3 (First Letters / Title):   INF-06, INF-07 → VES-08..11
Track 4 (Galen):                   INF-04, INF-05 → GAL-01..03
Track 5 (Dresden):                 DRE-01..05  (gated on file provision)
Track 6 (Rust / scale):            INF-08..10 → GPZ-06
Track 7 (Grand Prize study):       GPZ-01..05
Tracks are independent; run any order after their INF inputs pass.
```

**HUMAN-gated nodes (only the researcher can clear):** VES-06 (licence +
public flip), VES-07 (Discord registration + submission form), GPZ-04
(segmentation-path decision), SEL-02 (Bodleian outreach), SIN-01 (UCLA
registration), DRE-01 input (provide SLUB scan set), plus 10-minute
HUMAN-VERIFY sub-gates on ARC-03 and GAL-02 annotations.

**Deadlines:** Progress Prize 2026-08-31 23:59 PT · Grand Prize / First
Letters / Title 2027-06-25 23:59 PT.

---

# PHASE INF — shared infrastructure

## NODE-INF01 — Environment + manifest verification
- **Type:** GATE  **Size:** XS
- **Inputs:** repo root, MANIFEST.md, run_all.py
- **Output:** entry in docs/executioner_dag.md (versions + baseline)
- **Gate:** `python3 run_all.py` exits 0 at 2,585,391 checks / 0 failures;
  python3/numpy/Pillow versions recorded; `git ls-files` inventory logged.
- **Status:** PENDING  **Float check:** N/A

## NODE-INF02 — 14-bit lane-set constants
- **Type:** IMPL  **Size:** S
- **Inputs:** cram_dsp/core.py, PROOFS.md P6
- **Output:** cram_dsp/core.py — `LANES_8BIT=(7,11,13)`,
  `LANES_14BIT=(11,13,17,19)`, `LANES_EXT=(7,11,13,17,19)` with the P6 bound
  table in the docstring; selective_delta/any_delta accept them unchanged.
- **Gate:** bounds match T10 output exactly; a1_lint PASS.
- **Status:** PENDING  **Float check:** PENDING

## NODE-INF03 — T11: 14-bit selective-Δ tier
- **Type:** TEST  **Size:** S
- **Inputs:** NODE-INF02, run_all.py
- **Output:** run_all.py (T11)
- **Gate:** synthetic 14-bit page (steps to ±16383): LANES_14BIT
  exact-selective at Δ=±1 with 100%/100%; (7,11,13) exhibits the d vs d+1001
  alias on a planted decoy; harness total grows, 0 failures.
- **Status:** PENDING  **Float check:** PENDING

## NODE-INF04 — Lattice-aware ingestion (KELD-14 seam)
- **Type:** IMPL  **Size:** S
- **Inputs:** cram_dsp/forensics.py (fingerprint), data/archimedes_caltarget.npz
- **Output:** cram_dsp/ingest.py — detect value-lattice gcd g; sealed cast
  `v//g` at the ingestion seam with a ledger receipt recording g; exact
  re-expansion `v*g` proves losslessness.
- **Gate:** detects g=4 on the caltarget stack; receipt written; roundtrip
  bit-exact; refuses non-integer input.
- **Status:** PENDING  **Float check:** PENDING

## NODE-INF05 — Ledger v2: acquisition receipts
- **Type:** IMPL  **Size:** S
- **Inputs:** cram_dsp/forensics.py
- **Output:** forensics.py — `record_acquisition(url, byte_range, sha256, nbytes)`
  chained like any op.
- **Gate:** re-fetch of a pinned Archimedes range reproduces the digest;
  chain head deterministic across two runs.
- **Status:** PENDING  **Float check:** PENDING

## NODE-INF06 — OME-Zarr integer chunk reader
- **Type:** IMPL  **Size:** M
- **Inputs:** vesuvius-challenge-open-data S3 (public, unsigned HTTPS);
  `.zarray` JSON per volume
- **Output:** cram_dsp/zarr_reader.py — parse .zarray, fetch chunk bytes,
  decode codec (blosc/zstd are lossless byte codecs — document that boundary),
  return integer arrays only; every fetch receipted via NODE-INF05.
- **Gate:** one chunk from an eligible masked volume (e.g. PHerc0800) fetched
  twice → identical digest; dtype is unsigned integer; a1_lint PASS
  (codec lib is byte-level, not arithmetic).
- **Status:** PENDING  **Float check:** PENDING

## NODE-INF07 — tifxyz mesh reader + nearest-integer render sampler
- **Type:** IMPL  **Size:** M
- **Inputs:** a small published segment (resolve from scrollprize.org data
  browser), NODE-INF06
- **Output:** cram_dsp/mesh_render.py — parse tifxyz (coordinates are float32
  GEOMETRY, not evidence: sealed cast to fixed-point integers ×1000 at
  ingestion with receipt); sample volume by NEAREST NEIGHBOR so every emitted
  value is a source voxel value; no interpolation of evidence, ever.
- **Gate:** rendered crop reproducible across two runs; emitted value set ⊆
  source voxel values (checked); receipt records the geometry cast.
- **Status:** PENDING  **Float check:** PENDING (geometry cast documented)

## NODE-INF08 — Golden-vector export
- **Type:** TEST  **Size:** S
- **Inputs:** cram_dsp/*
- **Output:** tests/golden_vectors.json — inputs/expected for k_map (all four
  dual tracks), tower_k, selective_delta, conv2d_exact (small), fwd53/inv53,
  rct, keld_map.
- **Gate:** vectors regenerate identically; committed.
- **Status:** PENDING  **Float check:** PENDING

## NODE-INF09 — Rust crate `cram-core`
- **Type:** SCAFFOLD  **Size:** L
- **Inputs:** NODE-INF08, canon formulas (PROOFS.md P1–P6)
- **Output:** rust/cram-core/ — lanes, K-Elim (star + general + tower), KELD,
  selective-Δ, NTT, 5/3 lifting; u64/i128 only.
- **Gate:** `cargo test` green; `grep -rn "f32\|f64"` returns 0 in src/;
  extended-Euclid inverse (no Fermat).
- **Status:** PENDING  **Float check:** PENDING

## NODE-INF10 — Rust ↔ Python equivalence gate
- **Type:** GATE  **Size:** S
- **Inputs:** NODE-INF08, NODE-INF09
- **Output:** rust/cram-core/tests/golden.rs + result table in docs/executioner_dag.md
- **Gate:** every golden vector byte-equal between implementations.
- **Status:** PENDING  **Float check:** PENDING

---

# PHASE ARC — Archimedes (Boards 1 & 2)

## NODE-ARC01 — Re-acquire pinned windows under receipts
- **Type:** WIRE  **Size:** S
- **Inputs:** tools/fetch_tiff.py, data/SHA256SUMS.txt, NODE-INF05
- **Output:** data/archimedes_forgery.npz, data/archimedes_control.npz
  (local, gitignored) + acquisition receipts
- **Gate:** SHA-256 matches the pinned sums exactly.
- **Status:** PENDING  **Float check:** N/A

## NODE-ARC02 — Band-registration audit (integer, no resampling)
- **Type:** TEST  **Size:** M
- **Inputs:** NODE-ARC01, transforms.conv2d_exact
- **Output:** analysis/arc_registration.py + docs/ARC_REGISTRATION.md
- **Gate:** per-band integer shift table (argmax of exact cross-correlation
  over ±8 px) with second-peak margins, both windows, all 15 bands. If margins
  indicate sub-pixel misalignment, DECLARE it as a stated limitation — A1
  forbids resampling correction. No band is silently "fixed".
- **Status:** PENDING  **Float check:** PENDING

## NODE-ARC03 — Annotation fixture, control window
- **Type:** IMPL  **Size:** S
- **Inputs:** NODE-ARC01, core.keld_map
- **Output:** data/arc_annotations.json — ≥20 undertext-stroke boxes, ≥20
  overtext boxes, ≥20 clean-substrate boxes (programmatically proposed from
  KELD strata + straddle marks)
- **Gate:** boxes in-bounds, categories disjoint, rendered proof sheet
  produced. **HUMAN-VERIFY sub-gate:** researcher eyeballs the proof sheet
  (~10 min) and flips `"verified": true`.
- **Status:** PENDING  **Float check:** PENDING

## NODE-ARC04 — Integer separation metric
- **Type:** IMPL  **Size:** S
- **Inputs:** NODE-ARC03
- **Output:** cram_dsp/metrics.py — undertext contrast, overtext suppression,
  and separation score as exact integer milli-ratios; METRICS.md §9 formatting.
- **Gate:** unit tests on synthetic strokes; a1_lint PASS.
- **Status:** PENDING  **Float check:** PENDING

## NODE-ARC05 — Incumbent foil renderers
- **Type:** IMPL  **Size:** M
- **Inputs:** baseline_float.py, PRIOR_ART.md §1 recipes
- **Output:** baseline_float.py — `knox_pseudocolor`, `sharpie_subtract`,
  `pca_render` (float, QUARANTINED)
- **Gate:** renders produced on the control window; quarantine intact in lint.
- **Status:** PENDING  **Float check:** N/A (quarantine)

## NODE-ARC06 — CRAM renderers
- **Type:** IMPL  **Size:** M
- **Inputs:** NODE-INF02, NODE-INF04, transforms.py
- **Output:** cram_dsp/render.py — exact band-difference stack with tracked
  denominators, KELD strata composite (lattice-aligned), lane-comb undertext
  probe map on LANES_14BIT, reversible ChromaDI false colour; all receipted.
- **Gate:** digests reproducible across two runs; reversible paths carry
  round-trip receipts.
- **Status:** PENDING  **Float check:** PENDING

## NODE-ARC07 — Board 2 run: control head-to-head
- **Type:** TEST  **Size:** M
- **Inputs:** NODE-ARC03..06, data/archimedes_caltarget.npz
- **Output:** docs/ARCHIMEDES_CONTROL_RESULTS.md
- **Gate:** metric table — CRAM renders vs pseudocolor vs Sharpie vs PCA — on
  the annotated fixtures, with caltarget reference values; numbers ship
  whatever they are; every overlap scoped per the reporting rule.
- **Status:** PENDING  **Float check:** PENDING

## NODE-ARC08 — XRF reference acquisition
- **Type:** WIRE  **Size:** S
- **Inputs:** RIT mirror (locate XRF assets for folio 081r in
  Resources/metadL and pre-2007 trees; fall back to archimedespalimpsest.net)
- **Output:** data/arc_xrf/ + receipts + checksums
- **Gate:** XRF images for 081r on disk with provenance. If absent from both
  sources → BLOCKED, Requires: alternative source from researcher.
- **Status:** PENDING  **Float check:** N/A

## NODE-ARC09 — Board 1 run: the forgery window
- **Type:** TEST  **Size:** L
- **Inputs:** NODE-ARC01, NODE-ARC06, NODE-ARC08
- **Output:** docs/ARCHIMEDES_FORGERY_RESULTS.md
- **Gate:** KELD strata under overpaint, lane-comb class scans across all 15
  bands, cross-band residue-coherence map, exact-unmix attempts under a
  DECLARED linear overpaint model, Sqr-carry class maps — every positive
  claim corroborated against the XRF reference or explicitly marked
  UNCORROBORATED. A zero result ships as zero. Incumbent baseline on this
  window is zero; that context is stated, not implied.
- **Status:** PENDING  **Float check:** PENDING

## NODE-ARC10 — Boards 1–2 closure
- **Type:** REPORT  **Size:** S
- **Inputs:** NODE-ARC07, NODE-ARC09
- **Output:** BENCHMARKS.md + BOUNTIES.md status updates; commit + push
- **Gate:** boards show measured statuses with links to the two results docs.
- **Status:** PENDING  **Float check:** N/A

---

# PHASE VES — Vesuvius cash boards

## NODE-VES01 — Ink-label dataset acquisition
- **Type:** WIRE  **Size:** M
- **Inputs:** https://scrollprize.org/data_datasets#ink-labels-2026-07
  (resolve concrete URLs at run time), NODE-INF05
- **Output:** data/vesuvius/ink_labels/ + SHA256SUMS + receipts
- **Gate:** dataset on disk, integer dtypes confirmed, and a lattice /
  fingerprint characterization pass recorded (the first-contact measurement,
  same discipline as Archimedes §8 of METRICS.md).
- **Status:** PENDING  **Float check:** PENDING

## NODE-VES02 — Surface-label dataset acquisition
- **Type:** WIRE  **Size:** S
- **Inputs:** https://scrollprize.org/data_datasets#surface-labels-2026-07
- **Output:** data/vesuvius/surface_labels/ + receipts
- **Gate:** as NODE-VES01.
- **Status:** PENDING  **Float check:** PENDING

## NODE-VES03 — Exact-DSP evaluation on ink labels
- **Type:** TEST  **Size:** L
- **Inputs:** NODE-VES01, NODE-INF02/04, cram_dsp/metrics.py
- **Output:** docs/VESUVIUS_INK_EVAL.md + analysis/ves_ink_eval.py
- **Gate:** lane-comb / KELD / fingerprint feature maps scored against their
  labels — exact integer precision/recall per feature per fragment; any
  published baseline cited with scoped framing; no training, so
  train/predict overlap is structurally impossible (state it).
- **Status:** PENDING  **Float check:** PENDING

## NODE-VES04 — Reproducibility demo on THEIR data
- **Type:** TEST  **Size:** M
- **Inputs:** NODE-INF06, one eligible masked volume
- **Output:** docs/VESUVIUS_ZARR_DEMO.md + analysis/ves_zarr_demo.py
- **Gate:** stream N chunks → characterize → identical chain hash across two
  independent runs. This upgrades the Board B reproducibility claim from
  "our pipeline" to "their data".
- **Status:** PENDING  **Float check:** PENDING

## NODE-VES05 — Progress Prize packet
- **Type:** REPORT  **Size:** M
- **Inputs:** NODE-VES01..04, README.md, PROOFS.md, METRICS.md
- **Output:** docs/PROGRESS_PRIZE_SUBMISSION.md — problem addressed
  (reproducibility + exact evaluation + first-contact lattice findings),
  usage examples, community-format I/O, receipts-as-experiment-tracking.
- **Gate:** every submission criterion on scrollprize.org/prizes §Progress
  mapped to a section; packet complete. **Deadline 2026-08-31 23:59 PT.**
- **Status:** PENDING  **Float check:** N/A

## NODE-VES06 — Licence + visibility flip
- **Type:** GATE  **Size:** XS — **HUMAN**
- **Output:** LICENSE (MIT or researcher's choice); repo public
- **Gate:** researcher decision recorded. Required to ACCEPT a prize, not to
  submit — but early open-sourcing is an explicit judging criterion.
- **Status:** BLOCKED  **Requires:** researcher decision
- **Cascade:** none technically; scoring weight on VES-05.

## NODE-VES07 — Submission
- **Type:** GATE  **Size:** XS — **HUMAN**
- **Gate:** Discord registration + Google form submitted before deadline.
- **Status:** BLOCKED  **Requires:** researcher account actions

## NODE-VES08 — Published-segment acquisition (no-model route)
- **Type:** WIRE  **Size:** M
- **Inputs:** scrollprize data browser — published flattened renders/segments
  for Grand-Prize-eligible scrolls, NODE-INF07
- **Output:** data/vesuvius/segments/ + receipts
- **Gate:** ≥1 flattened render per targeted scroll with provenance; lattice
  pass recorded.
- **Status:** PENDING  **Float check:** PENDING

## NODE-VES09 — First Letters no-model ink-visibility pass
- **Type:** TEST  **Size:** L
- **Inputs:** NODE-VES08, NODE-ARC06 render tools
- **Output:** docs/FIRST_LETTERS_SCAN.md + programmatic images w/ scale bars
- **Gate:** exact contrast recovery (reversible stretches, KELD strata,
  lane-comb class maps) over every acquired render; any candidate with ≥10
  letterform-scale marks in a 4 cm² window flagged into a papyrology-facing
  packet; else a shipped negative. False-positive statement: nothing is
  generated, by construction. The prize page sanctions this exact route:
  directly visible ink with no model qualifies.
- **Status:** PENDING  **Float check:** PENDING

## NODE-VES10 — PHerc. Paris 4 title-region acquisition
- **Type:** WIRE  **Size:** M
- **Inputs:** data browser PHercParis4 (all volumes, incl. 2.4 µm), any
  published title-region meshes, NODE-INF06/07
- **Output:** data/vesuvius/paris4_title/ + receipts
- **Gate:** acquired + first-contact lattice characterization.
- **Status:** PENDING  **Float check:** PENDING

## NODE-VES11 — Title scan: different-ink-chemistry residue differential
- **Type:** TEST  **Size:** L
- **Inputs:** NODE-VES10, NODE-INF02
- **Output:** docs/TITLE_SCAN.md
- **Gate:** residue-class differential maps across z-slabs of the title
  region — the hypothesis is that a different ink is a different density
  class, not a different brightness. Candidates carry corroboration
  standards; a negative ships. No deadline pressure (prize stays open until
  won).
- **Status:** PENDING  **Float check:** PENDING

---

# PHASE GPZ — Grand Prize path (decomposed; decision-gated)

## NODE-GPZ01 — VC3D + spiral-fitter reproduction study
- **Type:** TEST  **Size:** M
- **Inputs:** github.com/ScrollPrize/villa (volume-cartographer), their
  tutorials
- **Output:** docs/GPZ_VC3D_STUDY.md
- **Gate:** VC3D built; spiral-fit tutorial reproduced on a public example;
  the winding-constraint data model documented from source.
- **Status:** PENDING  **Float check:** N/A (their stack)

## NODE-GPZ02 — Winding-constraint ↔ K-winding bridge study
- **Type:** REPORT  **Size:** M — GATED-SPECULATIVE
- **Inputs:** NODE-GPZ01, canon (K = winding number over the covering space)
- **Output:** docs/GPZ_WINDING_BRIDGE.md
- **Gate:** formal mapping of same/different-winding annotations to
  congruence classes; promoted only if the mapping survives worked examples
  from NODE-GPZ01 — otherwise recorded as a documented negative.
- **Status:** PENDING  **Float check:** N/A

## NODE-GPZ03 — Exact winding-consistency checker
- **Type:** IMPL  **Size:** L
- **Inputs:** NODE-GPZ02 (if promoted), NODE-INF07
- **Output:** cram_dsp/winding_check.py
- **Gate:** catches planted winding violations on a synthetic spiral
  exhaustively; runs on the NODE-GPZ01 example; integer homology counts only.
- **Status:** PENDING  **Float check:** PENDING

## NODE-GPZ04 — Segmentation-path decision
- **Type:** GATE  **Size:** XS — **HUMAN**
- **Gate:** researcher chooses: (a) team with an existing segmentation group
  as the exactness/verification layer, (b) build on the spiral fitter,
  (c) defer the Grand Prize. Decision recorded in docs/executioner_dag.md.
- **Status:** BLOCKED  **Requires:** researcher decision
- **Cascade:** NODE-GPZ05, NODE-GPZ06

## NODE-GPZ05 — VC3D integration of checker + exact renders
- **Type:** WIRE  **Size:** L
- **Inputs:** NODE-GPZ03, NODE-GPZ04(=a or b)
- **Gate:** checker + render path callable from VC3D flow on a real segment.
- **Status:** BLOCKED (on GPZ04)  **Float check:** PENDING

## NODE-GPZ06 — Teravoxel throughput
- **Type:** WIRE  **Size:** L
- **Inputs:** NODE-INF09/10, NODE-INF06
- **Gate:** Rust path streams a full masked volume's chunk set with chain
  hash equal across two runs; throughput recorded.
- **Status:** BLOCKED (on GPZ04)  **Float check:** PENDING

---

# PHASE GAL — Syriac Galen (Board 4)

## NODE-GAL01 — SGP folio acquisition
- **Type:** WIRE  **Size:** M
- **Inputs:** openn.library.upenn.edu/Data/0014/GalenSyriacPalimpsest/
  (CC BY), NODE-INF05
- **Output:** data/galen/ (≥5 bifolia, raw multispectral) + SHA256SUMS +
  receipts
- **Gate:** on disk, checksummed, first-contact lattice pass recorded.
- **Status:** PENDING  **Float check:** PENDING

## NODE-GAL02 — Annotation fixture (2 folios)
- **Type:** IMPL  **Size:** S
- **Output:** data/gal_annotations.json + proof sheet
- **Gate:** as NODE-ARC03, incl. the HUMAN-VERIFY sub-gate.
- **Status:** PENDING  **Float check:** PENDING

## NODE-GAL03 — Board 4 run: first quantitative score on SGP
- **Type:** TEST  **Size:** L
- **Inputs:** NODE-GAL01/02, NODE-ARC04..06
- **Output:** docs/GALEN_RESULTS.md
- **Gate:** metric table, CRAM renders vs implemented foils (PCA,
  pseudocolor, subtraction), scope stated plainly: their eight methods were
  ranked visually and never scored — this is the first numeric benchmark on
  the corpus, over the foils actually implemented. Numbers ship whatever
  they are.
- **Status:** PENDING  **Float check:** PENDING

---

# PHASE DRE — Dresden Codex (Board 5)

## NODE-DRE01 — Scan ingestion + characterization
- **Type:** WIRE  **Size:** M
- **Inputs:** SLUB scan set (**HUMAN provides** files/URLs; SLUB
  Mscr.Dresd.R.310 as fallback source), NODE-INF04/05
- **Output:** data/dresden/ + receipts + per-page lattice/fingerprint maps
- **Gate:** every page characterized before any analysis touches it.
- **Status:** BLOCKED  **Requires:** researcher provides the scan set (or
  approves the SLUB fetch)

## NODE-DRE02 — Repair-seam map, codex-wide
- **Type:** TEST  **Size:** M
- **Inputs:** NODE-DRE01, forensics.quant_fingerprint_map
- **Output:** docs/DRESDEN_SEAMS.md
- **Gate:** seam blocks enumerated with coordinates + panel images; receipts.
- **Status:** BLOCKED (on DRE01)

## NODE-DRE03 — Cross-generation copy-move (P75–P78 identity)
- **Type:** TEST  **Size:** L
- **Inputs:** NODE-DRE01 + Förstemann facsimile scans (public domain —
  locate, receipt, checksum as a sub-step)
- **Output:** docs/DRESDEN_P75_IDENTITY.md
- **Gate:** exact block matches across scan generations enumerated; the
  page-identity evidence reported at size against the standing P75–P78
  blocker.
- **Status:** BLOCKED (on DRE01)

## NODE-DRE04 — KELD strata + tonal-window hidden-layer scan
- **Type:** TEST  **Size:** M
- **Inputs:** NODE-DRE01; route the archeoastronomy-codex skill's evidence
  standards
- **Output:** docs/DRESDEN_STRATA.md
- **Gate:** per that skill — pattern-level evidence with panels; discovery
  mode (extract structure), not refutation framing.
- **Status:** BLOCKED (on DRE01)

## NODE-DRE05 — P54–56 eclipse-cell pass
- **Type:** TEST  **Size:** M
- **Inputs:** NODE-DRE01/04
- **Output:** docs/DRESDEN_P54_56.md
- **Gate:** cell readings + receipts, cross-referenced to the eclipse-table
  canon.
- **Status:** BLOCKED (on DRE01)

---

# PHASE SEL / SIN — acquisition-gated boards

## NODE-SEL01 — Codex Selden RGB preliminary pass
- **Type:** TEST  **Size:** M
- **Inputs:** Digital Bodleian, MS. Arch. Selden. A. 2 (open RGB scans),
  NODE-INF04/05
- **Output:** docs/SELDEN_RGB_PASS.md
- **Gate:** lattice/fingerprint + KELD on the RGB scans, with the limit
  stated plainly: RGB is not hyperspectral; this pass characterizes and
  triages, it does not claim under-gesso recovery.
- **Status:** PENDING  **Float check:** PENDING

## NODE-SEL02 — Hyperspectral-cube outreach
- **Type:** GATE  **Size:** XS — **HUMAN**
- **Gate:** researcher contacts Bodleian / Leiden (Snijders) for the 2016
  hyperspectral cubes; response recorded.
- **Status:** BLOCKED  **Requires:** researcher outreach

## NODE-SIN01 — Sinai Palimpsests registration
- **Type:** GATE  **Size:** XS — **HUMAN**
- **Gate:** free scholarly registration at the UCLA access site completed.
- **Status:** BLOCKED  **Requires:** researcher account

## NODE-SIN02 — Sinai pilot pass
- **Type:** TEST  **Size:** M
- **Inputs:** NODE-SIN01, one palimpsest's spectral set
- **Output:** docs/SINAI_PILOT.md
- **Gate:** first-contact characterization + one undertext probe run;
  numbers ship whatever they are.
- **Status:** BLOCKED (on SIN01)

---

# PHASE REP — campaign closure

## NODE-REP01 — Boards refresh
- **Type:** REPORT  **Size:** S
- **Inputs:** all completed TEST nodes
- **Output:** BENCHMARKS.md + BOUNTIES.md rewritten from measured statuses
- **Gate:** every board shows state (a) or (b) per the 100% definition; no
  ambiguous rows remain.
- **Status:** PENDING

## NODE-REP02 — Campaign checkpoint
- **Type:** REPORT  **Size:** XS
- **Output:** checkpoint block appended to docs/executioner_dag.md
  (completed / in-progress / pending / files-to-deliver, per skill format)
- **Status:** PENDING

## NODE-REP03 — Tag + push
- **Type:** GATE  **Size:** XS
- **Gate:** all changes committed; `v0.2.0` tagged; pushed to
  Skyelabz210/cram-dsp.
- **Status:** PENDING

---

## DEPENDENCY EDGES (compact)

```
INF01 → everything
INF02 → INF03, ARC06, VES03, VES11
INF04 → ARC06, VES01, GAL01, DRE01, SEL01
INF05 → ARC01, VES01/02/08/10, GAL01, DRE01
INF06 → VES01(opt), VES04, VES10, GPZ06        INF07 → VES08, GPZ03
INF08 → INF09 → INF10 → GPZ06
ARC01 → ARC02/03/06 → ARC07;  ARC03 → ARC04;  ARC05 → ARC07
ARC06+ARC08 → ARC09;  ARC07+ARC09 → ARC10
VES01 → VES03 → VES05;  VES04 → VES05;  VES05 → VES07(HUMAN);  VES06(HUMAN)∥
VES08 → VES09;  VES10 → VES11
GPZ01 → GPZ02 → GPZ03;  GPZ04(HUMAN) → GPZ05, GPZ06
GAL01+GAL02 → GAL03
DRE01 → DRE02/03/04 → DRE05
SIN01 → SIN02
ALL TEST/REPORT → REP01 → REP02 → REP03
```

52 nodes. 6 HUMAN-gated (+2 HUMAN-VERIFY sub-gates). 1 hard deadline:
2026-08-31 (Track 1). Everything else is patience and gates.
