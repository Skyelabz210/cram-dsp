# BENCHMARKS

Two layers: the **internal suite** (T1–T10, deterministic, reproducible by anyone
with the repo) and the **external scoreboard** (real artifacts with documented
prior failures, where the comparators' own published positions are the bar).

---

## 1. Internal suite — `run_all.py`

Deterministic and seeded. Reproduce with `python3 run_all.py`; it writes
`demo/RESULTS.md`, `demo/receipts.json`, and demo PNGs, and exits nonzero on any
gate failure.

| Tier | What it benchmarks | Scale | Result |
|---|---|---|---|
| **T1** | Dual-Track K-Elimination: star pairs, composite/composite pairs, star-family `c`-rule, tower | 2,169,024 checks (exhaustive where feasible) | PASS |
| **T2** | KELD stratification, 8-bit and 16-bit, plus pixel-perfect band recovery | 65,792 + 256 + full page | PASS |
| **T3** | Shadow-lane probes: straddle lemma, Sqr-carry fire sets, lane-comb selectivity, alias rejection, blind-spot closure, float-erasure survivability | exhaustive + controlled ground truth | PASS |
| **T4** | Integer NTT convolution vs unbounded-int oracle, INV-8 check lane, determinism digest | 30 random convolutions + check lane | PASS |
| **T5** | Reversible transduction layer (5/3 lifting 1-D/2-D multilevel, RCT, ChromaDI) and Kill #113 | 400 + 18 configs + 200,000 triples + 100 skew cases | PASS |
| **T6** | Rational-Grid Exact Unmixing vs float PCA foil, plus blind `(p,q)` estimation | full image pair | PASS |
| **T7** | Provenance: round-trip receipt, cross-run chain-hash equality | 2 independent pipeline runs | PASS |
| **T8** | Exact copy-move clone localization | full image, 49 block pairs | PASS |
| **T9** | Quantization-fingerprint splice localization (off-grid mask) + float erasure | block-level IoU | PASS |
| **T10** | Lane sizing vs source bit depth; aliasing bound and its tightness | 3 lane sets | PASS |
| **Lint** | A1 static compliance over all production files | every run | PASS |
| **Total** | | **2,585,391 checks** | **0 failures** |

### Standing internal figures

| Benchmark | Figure |
|---|---|
| Lane-comb selective-Δ, precision / recall | 100.000% / 100.000% (114/114) |
| Classical any-difference baseline, precision | 27.272% (114/418) |
| Exact unmixing error (recto / verso) | 0 / 0 |
| Float PCA foil error (recto / verso) | MAE 2.296 / 4.899 |
| Δ=1 evidence surviving one float blur | 88/114, plus 682 contaminating fires |
| Δ=1 evidence surviving CRAM round trip | 114/114, 0 contamination |
| Fingerprint blocks surviving one float blur | 0/28 |
| Fingerprint blocks surviving CRAM round trip | 28/28 |
| Copy-move IoU | exact (intersection = union) |
| Splice block IoU (off-grid mask) | 20/20 |
| Cross-run provenance chain equality | identical |

---

## 2. External scoreboard — real artifacts

Selection rule: prefer artifacts where **prior analysis is documented to have
failed**, so the bar is a published position rather than a self-set target.

### Board 1 — Archimedes Palimpsest, forged Evangelist folios · **OPEN**

- **Artifact:** folio 081r-088v (St. Mark forgery over Archimedes text); acquired,
  checksummed, 15 bands.
- **Incumbent position:** optical multispectral recovers **nothing**; the project
  escalated to synchrotron XRF at SLAC SSRL.
- **Status:** data acquired; engine not yet run on this window.
- **Scoring:** any residue-native separation above zero is new ground. Result will
  be reported at the size the evidence supports, including zero.
- **Already measured:** the 14-bit lattice (70,350,000 values, 0 exceptions,
  per-band gcd exactly 4) — a property of the artifact the incumbent processing
  chain cannot observe, since normalization destroys the lattice immediately.

### Board 2 — Archimedes control window · **OPEN**

- **Artifact:** ordinary palimpsest text on the same bifolio, with the in-frame
  calibration target committed as `data/archimedes_caltarget.npz`.
- **Incumbent position:** pseudocolor / Sharpie / PCA succeed and are readable.
- **Scoring:** head-to-head on the same folio, with exact reference values from
  the calibration target. Axes: exactness, reversibility, reproducibility,
  survivability.

### Board 3 — Reproducibility challenge · **CLAIMED (internal), UNVALIDATED (external)**

- **Bar:** the Vesuvius Challenge posted workflow reproducibility at
  collection scale as an unsolved problem (July 2026 open problems).
- **Position:** solved on this framework's own pipeline (identical chain hash
  across independent runs, P12). Integration with their stack is unbuilt, so the
  claim is scoped to this pipeline until it runs on their data.

### Board 4 — Syriac Galen Palimpsest · **QUEUED**

- **Artifact:** full multispectral release, CC BY, at digitalgalen.net / OPenn.
- **Incumbent position:** eight dimensionality-reduction methods ranked
  **visually**, no numeric score; illegible regions forced synchrotron XRF.
- **Scoring opportunity:** supply the first quantitative score on that corpus.

### Board 5 — Dresden Codex · **QUEUED**

- Program-internal open items (page identity P75–P78, P54–56 eclipse cells,
  repair seams). The KELD pigment ladder was written for this artifact; the new
  additions are fingerprint-discontinuity seam detection and exact copy-move
  across scan generations.

---

## 3. Benchmark integrity rules

1. **No self-set bars.** External boards use a comparator's published position.
2. **Exhaustive is labelled exhaustive.** Sampled results carry their draw count.
3. **Negative results ship.** A board that returns zero is reported as zero and
   stays on the scoreboard.
4. **Scoped, never bare.** Where a figure overlaps an existing method, the axis,
   the conditions, and the location of the differentiation are all stated —
   see `COMPARISONS.md`.
5. **Foils are quarantined, not suppressed.** The float comparators live in
   `baseline_float.py`, are excluded from A1 lint by name, and their errors are
   reported as measured.
6. **Every figure is reproducible from the repo** — deterministic seeds, pinned
   data checksums, and a fetch tool for the uncommitted rasters.
