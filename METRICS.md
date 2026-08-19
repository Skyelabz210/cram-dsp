# METRICS

The measurement contract. Every number here is produced by `run_all.py` or by an
acquisition pass over real data, and every one is an exact integer count or an
integer-formatted ratio — no floating-point statistics anywhere in the reporting
path (the float figures that appear are *the classical foils' own* errors).

---

## 1. Scoring axes

An axis is only reported when it can be scored. Where a result overlaps existing
methods it is reported **fully scoped** — the axis named, the exact conditions
stated, and the differentiation located — never as a bare verdict.

| Axis | Definition | Incumbent's position |
|---|---|---|
| **A. Exactness** | Deviation from ground truth, in source units | Float methods: nonzero residual by construction |
| **B. Reversibility** | Can the original bytes be recovered from the processed state? | Not offered; pipelines are one-way |
| **C. Reproducibility** | Do two independent runs commit to the same hash? | Not offered; float output is toolchain-dependent |
| **D. Selectivity** | Precision/recall of a probe against known ground truth | Reported by eye, if at all |
| **E. Evidence survivability** | What fraction of forensic structure survives one pass? | Erased silently |
| **F. Alias rejection** | Are confounders in one channel rejected by the others? | Single-channel methods cannot |

---

## 2. Substrate correctness (T1, T2, T5, T10)

| Measurement | Result | Scope |
|---|---|---|
| K-Elimination, star pair (36, 37) | exact on all 1,332 values | exhaustive |
| K-Elimination, Fermat-adjacent (256, 257) | exact on all 65,792 values | exhaustive |
| K-Elimination, composite/composite (1800, 1001) | exact on all 1,801,800 values | exhaustive |
| K-Elimination, (30030, 30031) | exact on 200,000 draws | random |
| Star-family inverse rule `A − c` | matches extended Euclid, `c = 1..200` | exhaustive in range |
| Tower (36, 37, 73) | `K` and `X` exact on all 97,236 values | exhaustive |
| KELD 8-bit / 16-bit | `K = floor(L/M)` on all 256 / all 65,536 | exhaustive |
| Reversible transforms | bit-exact round trip | 400 1-D, 18 2-D configs, 200k RCT triples, 5-band ChromaDI |
| Kill #113 `⟨I, D I⟩` | exactly 0 | 50 images × 2 axes |
| Lane-comb aliasing | none within the proven bound | 3 lane sets, bound shown tight |
| **Harness total** | **2,585,391 checks, 0 failures** | — |

---

## 3. Probe performance on controlled ground truth (T3)

Synthetic palimpsest: Δ=+1 undertext on a posterized substrate with Δ=+11 and
Δ=+12 decoy strokes and plateau steps of +4.

| Probe | Precision | Recall | Notes |
|---|---|---|---|
| Lane-comb selective ±1, lanes (7,11,13) | **100.000%** (114/114) | **100.000%** (114/114) | zero false fires |
| Classical any-difference (\|d\| ≥ 1) | 27.272% (114/418) | 100.000% | plateau steps and both decoys fire |
| σ-11 alone, selective ±1 | — | — | **aliases all 8 Δ=12 decoy edges** (12 ≡ 1 mod 11); comb rejects all 8 |
| σ-11 alone, any-difference | — | 0/8 | **blind to Δ=11**; comb catches 8/8 |

Scoped honestly: on a pristine full-width integer image a classical band-pass
`|d| == 1` could match the comb's numbers. The differentiators are (i) the probe
runs on lane trays with the full-width image absent — verified identical output,
where a magnitude-thresholding detector has no input at all; (ii) CRT alias
rejection, which no single channel can do; (iii) survivability, below.

---

## 4. Evidence survivability (T3, T9) — axis E

| Operation | Δ=1 ink edges retained | Contaminating false fires | Quantization-fingerprint blocks retained |
|---|---|---|---|
| CRAM-DSP wavelet round trip | **114/114 (100%)** | 0 | **28/28 (100%)** |
| One float Gaussian blur + round, σ=1 | 88/114 (77.192%) | **682** | **0/28** |
| One float blur + round, σ=2 | 73/114 (64.035%) | 1,291 | — |

A single classical operation destroys 26 ink edges irrecoverably, injects 682
artifact fires into the Δ=1 class, and erases the entire requantization history.
The A1 path loses nothing, and the loss is *provably* nothing (P11, P12).

---

## 5. Separation accuracy (T6) — axis A

| Method | Recto error | Verso error |
|---|---|---|
| Rational-Grid Exact Unmixing at true (p,q) | **0** (exact equality, 0 divisibility violations) | **0** |
| Float PCA blind separation, best affine fit | MAE 2.296 | MAE 4.899 |

Scope: exactness holds given a rational mixing operator; the blind estimator
searches the coprime grid `q ≤ 12` and recovered (3,8) unaided.

---

## 6. Localization (T8, T9) — axis A

| Task | Result |
|---|---|
| Copy-move clone detection | IoU **exact** (intersection = union = planted region), 49 block pairs |
| Splice localization, mask deliberately off the block grid | block IoU **20/20**; background step estimated as 4; seam blocks self-flag at gcd 1 |

---

## 7. Reproducibility (T7) — axis C

| Measurement | Result |
|---|---|
| Round-trip receipt (original bytes recovered) | true |
| Two independent runs → identical chain head | **yes** |
| Chain head (this build) | `b4f88f95d97ff211…` |

This is the axis on which no comparator competes at all, and the one the Vesuvius
Challenge posted as unsolved (`PRIOR_ART.md` §3).

---

## 8. Real-artifact measurements — Archimedes Palimpsest

Acquired 2026-08-19 from the RIT mirror by remote-IFD parsing + HTTP range
requests. Windows: `forgery` (inside the forged St. Mark painting — where the
incumbent optical stack recovers nothing), `control` (ordinary palimpsest text on
the same bifolio), `caltarget` (in-frame reflectance target).

**First measurement, before any processing — the 14-bit lattice.**

| Check | Result |
|---|---|
| Sample values examined | **70,350,000** (15 bands × 3 windows) |
| Values not divisible by 4 | **0** |
| Per-band value-lattice gcd | exactly 4, all 15 bands, both windows |
| Minimum observed step | 4 |

**Conclusion:** the published 16-bit release is **14-bit sensor data
left-shifted into a 16-bit container**. True dynamic range is 0–16,383; two bits
are padding. Consequences: (i) any tool reporting 16-bit precision on this data
is reporting two bits of padding; (ii) the KELD ladder must run on `v/4`, or on
STAR16 with the lattice declared, so band boundaries land on real quantization
levels; (iii) by P6, 14-bit evidence requires lane product > 32,766 — the
`{7,11,13}` comb (P = 1,001) is **insufficient**, and the Safe Basis extenders
`{17,19}` become load-bearing: `{11,13,17,19}` gives P = 46,189 (B = 23,094).

This was produced by the framework's own fingerprint statistic on first contact
with the data. A float pipeline cannot observe it — normalization destroys the
lattice in its first operation.

---

## 9. Reporting rules

1. Every reported figure traces to a named test in `RESULTS.md` or an acquisition
   pass recorded here.
2. Exhaustive is stated as exhaustive; sampled is stated with its draw count.
3. Overlap with existing methods is reported with the axis, the conditions, and
   the location of the differentiation — never as a bare "on par."
4. Calibrations that ride on top of an exact result (e.g. the pigment table over
   the exact KELD index) are labelled as calibration, not as theorem.
5. Percentages are computed by integer division and printed with fixed decimals;
   no float appears in the reporting path.
