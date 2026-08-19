# Evaluation Protocols Reference (dsp-analyst)

How results are scored, corroborated, and reported in this program. This file
operationalizes the house law; METRICS.md in the repo is the binding contract,
this is the analyst's working procedure.

## 1. The measurement contract (summary)

- Six axes: **A** exactness · **B** reversibility · **C** reproducibility ·
  **D** selectivity (precision/recall vs ground truth) · **E** evidence
  survivability · **F** alias rejection. Score only axes that can be scored.
- Every figure traces to a named test or receipted acquisition pass.
- Exhaustive labeled exhaustive; sampled carries its draw count.
- Integer reporting: percentages by integer division; foil errors in the
  foil's own units, clearly attributed to the foil.
- Theorem vs calibration labeling is mandatory (exact index vs pigment
  table).

## 2. Ground truth & fixture design

Synthetic (engine development): planted ground truth with decoys and
confounders *designed to fool the method* (Δ-aliases, off-grid masks, flat
blocks); exhaustive where feasible.

Real artifacts (no oracle exists):

1. **Annotation fixtures** — programmatically proposed stroke / overtext /
   substrate boxes from exact statistics (KELD strata, class maps), then a
   HUMAN-VERIFY gate (researcher eyeballs a proof sheet, flips
   `verified: true`). Categories disjoint; coordinates committed; the
   fixture file is itself receipted.
2. **In-frame references** — embedded calibration targets (grayscale /
   reflectance patches) give exact expected relationships; use them as the
   anchor for any contrast or linearity claim.
3. **Cross-modality references** — where an independent modality exists
   (XRF for iron-gall ink), it is the corroboration oracle for optical
   claims.
4. **Held-out discipline** — no training here, so overlap is structurally
   impossible; still verify probes on labeled regions distinct from the
   regions used to design fixtures, and say so.

Anti-pattern: inventing a metric after seeing the result it flatters. Metric
definitions are committed before the scoring run (the DAG's gate text is the
commitment).

## 3. Corroboration ladder (claims on documented-failure targets)

Where the incumbent recovered nothing (Archimedes forgery folios, Paris 4
title region), a positive claim requires:

1. The finding reproduces bit-identically (chain hash) across runs — floor
   requirement, automatic under A1.
2. The finding survives a *designed adversary*: show the same statistic on
   matched control regions where no undertext exists; report both.
3. Independent-modality corroboration (XRF, alternate band family,
   different physical statistic) — or the claim ships marked
   **UNCORROBORATED** in the results doc and stays off the boards.
4. Papyrology/epigraphy review for legibility claims (letters are judged by
   readers, not by the engine).

Negative results ship with the same care: the conditions under which zero
was measured are stated precisely enough to be re-run.

## 4. Head-to-head scoring procedure

1. Identical input, identical fixtures, for every method.
2. Incumbent foils implemented faithfully from their published recipes,
   quarantined, and run at their best plausible settings (never strawmanned;
   if a foil needs an operator-tuned threshold, tune it in the foil's favor
   and record the setting).
3. Integer separation metrics (contrast ratios, suppression ratios,
   precision/recall) per fixture category.
4. Table published with every overlap scoped: axis, conditions, where the
   differentiation lives. Where the incumbent wins an axis, that row says
   so plainly (COMPARISONS.md §7 is the model).

## 5. Report templates

**Results doc (heritage / boards):**
1. Artifact & acquisition (receipts, checksums, capture metadata)
2. First-contact characterization (lattice, registration, fingerprints)
3. Methods (exact operators used; foil recipes; fixture design)
4. Results (tables; panels; per-axis)
5. Scoped comparisons
6. Limitations & declared boundaries (e.g., sub-pixel misalignment declared,
   not corrected)
7. Negative findings
8. Reproducibility package (commands, seeds, chain heads)

**Court-facing examination report adds:**
- Examiner qualifications & role; evidence handling (hashes at intake,
  storage, transfer)
- Tool validation notes (versions; the reproducibility certificate)
- Examination narrative in SWGDE task vocabulary (integrity vs
  authentication vs provenance findings kept distinct)
- Conclusions strictly in supports / is-inconsistent-with form, with the
  asymmetry stated (absence of detected manipulation ≠ authenticity)
- Appendices: receipts.json, fixture files, panel exhibits with scale bars

## 6. Quick checklists

**Before any claim:** receipted? characterized first? metric pre-committed?
exhaustive-or-count stated? scoped against incumbents? corroborated or
marked? limitations section written?

**Before any report ships:** integer-only reporting path? theorem vs
calibration labels? negatives included? chain heads printed? every figure
traceable to a test name? incumbent-wins rows present where true?
