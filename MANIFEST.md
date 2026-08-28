# MANIFEST

Complete inventory. Status vocabulary: **VERIFIED** (gate passed, exhaustive or
stated-sample test in `demo/RESULTS.md`), **QUARANTINED** (float by design,
comparison foil only, never on a production path), **ACQUIRED** (external data,
checksummed), **RECORD** (session/administrative document).

---

## Framework — `cram_dsp/`

| File | Contents | Status | Gate |
|---|---|---|---|
| `core.py` | Safe Basis S6/S8, typed lanes, `DualTrack` star-family K-Elimination, `tower_k`, KELD (8/16-bit), σ-fiber, `sqr_carry` (+ derived fire sets, lane-7 refusal), QR/QNR straddle, lane-comb `selective_delta` / `any_delta` | VERIFIED | T1, T2, T3, T10 |
| `transforms.py` | Integer NTT convolution over `P = 998244353`, direct oracle, `conv2d_modp` INV-8 check lane, Kill #113 skew witness, binomial kernels with exact denominators, `emit_round_div` seam, RCT, reversible ChromaDI, LeGall 5/3 lifting (1-D + multilevel 2-D) | VERIFIED | T4, T5 |
| `unmix.py` | Rational-Grid Exact Unmixing: `mix`, fraction-free `unmix_exact`, blind `estimate_pq` on the coprime grid | VERIFIED | T6 |
| `forensics.py` | `Ledger` (SHA-256 hash-chained receipts, round-trip receipts, JSON export), `copy_move_exact`, `quant_fingerprint_map`, `estimate_background_step`, `splice_flag_map`, `sigma_diff_histograms`, exact integer `iou` | VERIFIED | T7, T8, T9 |
| `synth.py` | Deterministic seeded integer evidence generators: faint palimpsest page (Δ=1 ink, Δ=11/Δ=12 decoys, plateau steps), codex strata page, recto-verso bleed pair, off-grid splice, copy-move | VERIFIED | used by T3, T6, T8, T9 |
| `baseline_float.py` | Classical foils: float PCA separation, best-fit MAE, Sobel, float Gaussian, `blur_round_int` | **QUARANTINED** | excluded from A1 lint by name |
| `a1_lint.py` | AST compliance scanner — float literals, true division, float names/attributes; quarantine and self-exemption discipline | VERIFIED | run inside every harness pass |
| `dresden.py` | The glyph machine: integer luma, integer Otsu (cross-multiplied), run-based 4/8-conn components, shift-OR dilation, glyph cells, circular-outward ring signatures (exact isqrt), sector codes (sequential octants) with exact dihedral matching, L1 matching + all-pairs matrix, luminance ordering, seeded permutation path test, exact hole counting (hollow/solid dot topology), exact quantile tonal bands, edge-orientation localizer (orientation_planes/pool_planes/cooccurrence_map/locate, mirror-aware), white-gradient machinery (order_stat/highlight_freeze/white_nodes/white_path), pigment classes (exact 4-way chroma partition), white-trail machinery (local_bright_field substrate-median field, filament_components, trail_polyline, trail_glyph_sequence), midrank_normalize (cross-generation confound removal), cooccurrence_normalized (exact integer cosine), decide_with_abstention (void rejection), node_records + three orderings + exact agreement metric | VERIFIED | dresden_run 636/0 · discover 9/0 · locate 6/0 · white 7/0 · vocab · seams 4/0 · strata 3/0 |
| `__init__.py` | Package surface | — | — |

## Harness

| File | Contents | Status |
|---|---|---|
| `run_all.py` | Tiers T1–T10 + A1 lint. Emits `demo/RESULTS.md`, `demo/receipts.json`, demo PNGs. Fully relocatable (paths resolve from the file's own location) | VERIFIED — **2,585,391 checks, 0 failures** |

Reproduce: `python3 run_all.py` (requires numpy, Pillow). Deterministic and seeded.

## Documentation

| File | Contents |
|---|---|
| `README.md` | Entry point, claims-at-a-glance, quick start |
| `PROOFS.md` | P1–P13 with proofs: K-Elimination, star-family inverse, adjacency collapse, KELD exactness, tower correctness, lane-comb selectivity + bit-depth sizing rule, QR/QNR straddle, Sqr-carry fire set, exact unmixing, Kill #113, reversibility, provenance certificate, A3 triviality |
| `METRICS.md` | Measurement contract, six scoring axes, every measured number, reporting rules |
| `PRIOR_ART.md` | Incumbent stack specs, documented failures on the target artifact, comparator programs, residue-arithmetic and forensic-imaging prior art |
| `COMPARISONS.md` | Head-to-head per axis, including where comparators are ahead |
| `BENCHMARKS.md` | The benchmark suite definition and current standings |
| `BOUNTIES.md` | Live prize targets (Vesuvius Grand Prize, First Letters, Title, Progress) with per-gate CLEARED / PARTIAL / NOT CLEARED audit, plus non-cash first-mover claims |
| `MANIFEST.md` | This file |
| `EXECUTION_DAG.md` | Campaign plan: 52 gated nodes across 9 phases covering every target board to 100% (executioner format) |
| `CLAUDE.md` | Agent instructions: axioms, gates, commands, record-keeping, HUMAN-gated node list |
| `docs/ARCHITECTURE.md` | Design document structured by the five verbs (ideate / innovate / design / test / build) |
| `docs/BASELINE_DOSSIER.md` | Archimedes acquisition record, prior-attempt failure record, incumbent stack table, comparator table |
| `docs/executioner_dag.md` | Build DAG: nodes, gates, statuses, checkpoint — the session record |
| `docs/CRAM_OPPORTUNITY_REPORT.md` | CRAM opportunity index over the classical forensic DIP surface (6 entries, FORCED/CANDIDATE, routing keys) |
| `docs/ARCHIMEDES_RESULTS.md` | Measured results, Boards 1 and 2: 14-bit lattice confirmed, registration audit, lane sizing on real deltas, survivability head-to-head (incl. the axis the incumbent wins), forgery-window shipped negative |
| `analysis/arc_run.py` | The Archimedes run: 75,564,310 exact checks, 0 failures |
| `docs/RULES_OF_EXPLORATION.md` | Researcher-set rules binding the Dresden track: no hypothesis closure while machinery is under construction; controls may not presuppose the hypothesis false; failed methods kept as receipts; evidence vs visualization; control battery; multi-path agreement; morphology before semantics |
| `docs/DRESDEN_MACHINE_STATUS.md` | Per-stage VALIDATED / BUILT-UNVALIDATED / NOT-BUILT table, the failures kept as receipts, and the list of nulls that must exist before the trail hypothesis can be leaned on |
| `docs/DRESDEN_WHITEFIELD.md` | White-field v2: evidence node records, three-path agreement per page, written-vs-bare comparison, cross-page trail continuity |
| `docs/DRESDEN_DOTS.md` | Dot morphology, unlabelled: 34,410 round marks measured, class separation figures, spacing regularity, recurrence ranking against the located p69 column |
| `docs/regions/` | Per-region reports: full lens stack + cross-codex matches (`pNN_yN_xN.md`), radial decompositions (`radial_pNN.md`) |
| `LICENSE` / `NOTICE.md` | MIT for code and skill; CC BY 4.0 for docs; CC BY 3.0 attribution for Archimedes data |
| `cram_dsp/ingest.py` | Lattice detection + sealed, receipted, exactly reversible entry seam |
| `cram_dsp/metrics.py` | Integer separation and survivability metrics (exact milli-units) |
| `cram_dsp/render.py` | Exact renderers: band difference, KELD composite, lane class maps, unit-step probe |
| `docs/survey_03r.png` | Whole-leaf survey of folio 081r-088v showing the forged Evangelist portrait and the palimpsest leaf |

## Data — `data/`

| File | Contents | Status |
|---|---|---|
| `archimedes_caltarget.npz` | 15 bands × 700 × 700, uint16 — the in-frame reflectance/greyscale calibration target | ACQUIRED (8.6 MB, included as fixture) |
| `SHA256SUMS.txt` | Checksums for all three acquired windows, including the two not committed | — |
| `dresden/source/wdl11621_codex_dresdensis.pdf` | The Dresden Codex, WDL item 11621 (SLUB Mscr.Dresd.R.310) — researcher-provided, committed whole per request for in-repo access | ACQUIRED (20.6 MB, SHA-256 pinned) |
| `dresden/pages/` (78 files) | Per-page JPEGs, byte-exact DCTDecode streams from the PDF — numbered scan01–scan78 | ACQUIRED (21 MB total, each pinned in `dresden/SHA256SUMS.txt`) |
| `dresden/INDEX.md` | Page index: scan ↔ Förstemann numbering + assumed section categories, blank-corroboration gated | RECORD |
| `dresden/characterization.json` | Exact integer per-page characterization (dims, luma stats, Otsu, ink coverage) | VERIFIED |
| `dresden/receipts.json`, `dresden/machine_receipts.json`, `dresden/queries/receipts.json` | Hash-chained acquisition/decode/analysis receipts | RECORD |
| `dresden/queries/` | Researcher's concept illustrations + photographed column, exact decimations, originals SHA-256-pinned | ACQUIRED |
| `dresden/derived/` | Galleries for every page: path overlays (`paths/`), dot overlays (`dots/`), tonal bands (`bands/`), white freeze/paths (`white/`), pigment + shadow (`pigment/`), KELD strata + tonal windows (`strata/`), seam candidates (`seams/`), white trails (`trails/`), form-family contact sheets (`clusters/`) — display-seam renders of receipted measurements | RECORD |
| `dresden/discovery_receipts.json` | Hash-chained per-page discovery-sweep receipts | RECORD |

**Not committed (regenerate with `tools/fetch_tiff.py`):**
`archimedes_forgery.npz` (46 MB — inside the forged St. Mark painting, where the
incumbent optical stack recovers nothing) and `archimedes_control.npz` (45 MB —
ordinary palimpsest text on the same bifolio). Both are byte-reproducible from the
public mirror; checksums above pin them. Kept out of git because large binaries in
version control are a liability, not because they are unavailable.

Provenance: RIT mirror of the Archimedes Palimpsest release
(`mirrors.rit.edu/archie/post-2007/HTML_TIFF/`), CC BY 3.0. Source rasters are
8160 × 10880 × 3 × 16-bit (532,690,516 bytes each), 15 bands per folio, 833 ppi,
imaged 2007-08-20 at the Walters Art Museum.

## Skills — `skills/`

| File | Contents |
|---|---|
| `skills/dsp-analyst/SKILL.md` | The ANALYST role: dual-layer doctrine (SWGDE-aligned forensic compliance + CRAM-DSP house law), four core workflows (first contact, authentication exam, recovery campaign, scoring/reporting), hard refusals |
| `skills/dsp-analyst/references/forensic-standards.md` | SWGDE document registry + exam methodology, PRNU caveats and transfer attacks, AI-generation screening layers, C2PA/provenance limits, admissibility posture |
| `skills/dsp-analyst/references/archaeo-imaging.md` | Modality catalog (MSI/HSI/XRF/RTI/DStretch/SfM/uCT/OCT), incumbent stack concessions, FADGI / ISO 19264-1 / Metamorfoze, per-corpus notes for all program targets |
| `skills/dsp-analyst/references/evaluation-protocols.md` | Measurement contract, fixture and ground-truth design, corroboration ladder for documented-failure targets, head-to-head procedure, report templates |
| `skills/dsp-analyst.skill` | Packaged artifact of the above (zip), ready to install via Save Skill — built with skill-creator's `package_skill.py` |

## Tools — `tools/`

| File | Contents |
|---|---|
| `fetch_tiff.py` | Remote TIFF IFD parser + HTTP range-request row-band fetcher. Pulls exact crops from the 532 MB rasters without downloading whole files, with no resampling or transcoding — the integers on disk are the integers the camera wrote |
| `extract_dresden.py` | DRE-01 ingestion: byte-exact extraction of the 78 embedded JPEG scans from the WDL 11621 PDF (raw DCTDecode streams, no re-encode), acquisition + decode receipts, integer per-page characterization |
| `build_dresden_index.py` | `data/dresden/INDEX.md` generator — Förstemann numbering + assumed section categories, gated on the measured blank-page corroboration |
| `pin_queries.py` | Pins the researcher-supplied illustration/query images as exact nearest-neighbour decimations with the originals' SHA-256 in receipts |

Usage: `python3 tools/fetch_tiff.py <folio> <band> <row0> <nrows> <col0>:<col1>`

## Outputs — `demo/`

`RESULTS.md` (full harness transcript), `receipts.json` (exported provenance
chain), and eight demo PNGs: KELD strata, isopleth silhouette, lane-comb ink map,
the same map after one float blur, unmixing triptych, copy-move mask, splice flag
panel, binomial emission.

---

## Axioms in force

- **A1 — zero float.** Statically enforced by `a1_lint` on every production file,
  every run. The single sanctioned rounding division is `emit_round_div` at the
  display seam.
- **A2 — reconstruction-free.** No Garner, no mixed-radix, no positional decode
  anywhere. Magnitude by K-Elimination (P1); `derive()` exists only for the
  emission seam.
- **A3 — distortion certification.** All production lane operators are standard
  CRT ring homomorphisms, so `F_eff = F_base` and `Γ = 1` (P13). The one
  non-homomorphic construct (`Sqr` on shadow lanes) is a read-only probe.
- **A8 — no Sqr on lane 7.** Enforced by refusal, not by warning.
- **DKAM.** `ρ = 3 > d = 2`; the torus stays subcritical.
- **Inverse guard.** Extended Euclid only (`pow(a, -1, m)`); Fermat's
  `pow(a, m-2, m)` is silently wrong on composite moduli and is never used.
