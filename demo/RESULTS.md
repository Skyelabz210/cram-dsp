# CRAM-DF — Verification Results

**2,585,391 exact checks — 0 failures.**
All arithmetic integer-exact (A1); no Garner/mixed-radix anywhere (A2); all lane
operators standard CRT homomorphisms, so the A3 distortion certificate is trivial
(Gamma = 1); the sanctioned Sqr probe runs on lanes 11/13 only, never lane 7.

## T1 — Substrate: Dual-Track K-Elimination (star family, composite, tower)
  substrate checks: 2,169,024

## T2 — KELD stratification (exact floor(L/M) via residue pair)
  111=3A isopleth silhouette pixels: 278 (K<3 vs K>=3 boundary; band map is exact, the pigment table is per-corpus calibration)

## T3 — Shadow lane probes (straddle, Sqr-carry, lane-comb selective-Δ)
  lane-comb (7,11,13) selective ±1: precision 100.000% (114/114), recall 100.000% (114/114 ink edges)
  residue-only regime: detection ran on the three lane trays with the full-width image absent — depth-1 per-lane equality tests, zero cross-lane data flow (A2/i.i.d. preserved). The classical band-pass |d|==1 has no d to threshold here: magnitude exists in no lane, and forming it is exactly the reconstruction step this substrate retires. The scoped equivalence above holds only when a pristine full-width integer image is available and nothing ever processes it.
  single-lane σ-11 selective ±1: 8/8 Δ=12 decoy edges falsely fire (12 ≡ 1 mod 11 alias) — cross-lane comb rejects all of them: 0
  Δ=11 blind spot: σ-11-only detector fires on 0/8 Δ=11 edges; lane-comb fires on 8/8
  classical any-difference baseline (|d|>=1): recall 100.000%, precision 27.272% (114/418 fires — plateau steps and decoys all fire). A classical integer band-pass |d|==1 could match the comb here; the CRAM contribution is doing it natively in residue lanes (never materializing d), CRT alias rejection, and A1 survivability below.
  after ONE classical float blur+round (sigma=1): recall 77.192% (88/114 — 26 ink edges irrecoverably lost) and precision 11.428% (682 blur-artifact ±1 fires contaminate the class); at sigma=2: recall 64.035%, 1291 false fires. The float path is irreversible; the CRAM path below loses zero.

## T4 — Integer NTT convolution (exact, check-laned, deterministic)
  kernel carried as exact (numerator, denominator=256); the single rounding division happens only at the emission seam

## T5 — Reversible transforms (Transduction layer) + Kill #113

## T6 — Rational-Grid Exact Unmixing vs float PCA
  estimator score (violations, negatives, cross-energy): (0, 0, 203126)
  float PCA baseline best-fit MAE: recto 2.296, verso 4.899 (intensity units) vs CRAM exact 0.000 — given a rational mixing operator; blind estimation is over the coprime grid q<=12

## T7 — Provenance: hash-chained receipts (computational chain of custody)
  chain head: b4f88f95d97ff21124578e47129457d3…  (3 receipts, receipts.json exported)

## T8 — Exact copy-move clone detection
  49 matching block pairs; detected mask == planted clone exactly

## T9 — Quantization-fingerprint splice localization + float erasure
  estimated background step: 4; block IoU 20/20 (interior fp=5, seam blocks collapse to gcd 1 — both flagged)
  background-fingerprint blocks before float blur: 28; after: 0 — one classical float op erases the requantization history irreversibly

## T10 — Lane sizing vs. source bit depth (Safe Basis selection theorem)
  (7, 11, 13): product 1,001 -> value-exact for |d| <= 500  DOES NOT cover 14-bit evidence (|d| <= 16,383)
  (11, 13, 17, 19): product 46,189 -> value-exact for |d| <= 23,094  covers 14-bit evidence (|d| <= 16,383)
  (7, 11, 13, 17, 19): product 323,323 -> value-exact for |d| <= 161,661  covers 14-bit evidence (|d| <= 16,383)
  => the 8-bit demos above run on (7,11,13); the 14-bit Archimedes rasters require the Safe Basis extenders {17,19} — S8 is load-bearing for real forensic bit depths, not decorative.

## A1 lint (static compliance)
  A1 LINT: PASS (all production files clean)
  __init__.py: A1 CLEAN
  a1_lint.py: 1 self-references (the detector names its target) — exempt
  baseline_float.py: 20 float sites — QUARANTINED (classical foil, float by design)
  core.py: A1 CLEAN
  forensics.py: A1 CLEAN
  synth.py: A1 CLEAN
  transforms.py: A1 CLEAN
  unmix.py: A1 CLEAN
