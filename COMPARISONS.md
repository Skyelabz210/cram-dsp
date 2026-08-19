# COMPARISONS

Head-to-head against everything this framework is running against. Each row names
the axis, the exact conditions, and where the differentiation lives. A comparator
"wins" an axis wherever it does — those are recorded too.

---

## 1. Against the incumbent manuscript-imaging stack

Easton / Knox / Christens-Barry — pseudocolor, Sharpie subtraction, PCA, XRF
escalation. The field standard.

| Axis | Incumbent | CRAM-DSP | Conditions |
|---|---|---|---|
| Band capture | **13 LED bands, Δλ ≤ 40 nm, raking illumination** — CRAM-DSP has no capture hardware | n/a | The incumbent owns acquisition outright; this framework is the *processing layer downstream of it* |
| Layer separation | pseudocolor / PCA, residual by construction | exact where the mixing operator is rational (0 error, P9) | Given a rational operator; blind grid `q ≤ 12` |
| Noise on subtraction | conceded: subtraction *"enhances any noise"* | skew operator has `⟨I, D I⟩ = 0` exactly (P10) | Different operator class, not a repair of theirs |
| Banding / stratification | by threshold on decoded magnitude | exact `floor(L/M)` from a residue pair (P4) | Exhaustive 8- and 16-bit |
| Reversibility | not offered | bit-exact, receipted (P11, P12) | 200k+ round trips |
| Reproducibility | not offered; visual judgement | identical chain hash across runs | Axis C |
| Method selection | per-leaf, operator preference (conceded) | fixed operators, no tuning | — |
| **Forgery folios** | **recovers nothing; requires synchrotron XRF** | untested on this window as of this commit | The open target; result will be reported at whatever size it earns |

**Honest position:** the incumbent's capture system is superb and is the input to
this framework, not a rival to it. The differentiation is entirely in processing:
exactness, reversibility, and reproducibility.

---

## 2. Against Vesuvius Challenge (ML ink detection + virtual unwrapping)

| Axis | Vesuvius | CRAM-DSP | Conditions |
|---|---|---|---|
| Reading sealed scrolls | **PHerc. 1667 read end-to-end, June 2026** — a result this framework has no equivalent of | n/a | They own the unwrapping and ink-detection problem |
| Scale | 300 TB/scroll, teravoxel volumes, OME-Zarr streaming | untested at that scale | Phase-2 work |
| Ink vs. no-ink-recovered | posted as **unsolved** | exact probes give a decidable answer per lane class, but unvalidated on their data | Claim not yet earned on scroll data |
| **Workflow reproducibility** | posted as **unsolved** in their July 2026 open problems | solved on this framework's own pipeline (P12, axis C) | Demonstrated on our data; integration with their stack unbuilt |

**Honest position:** their result is the headline achievement of the field. The
one axis where this framework has something they explicitly say they lack is
reproducibility — and that claim is only proven on our pipeline so far.

---

## 3. Against the Syriac Galen benchmark (8 dimensionality-reduction methods)

Comparator: GDA, LDA, NCA (supervised); GPLVM, Isomap, Landmark Isomap, PCA, PPCA
(unsupervised); plus CVA.

| Axis | Galen benchmark | CRAM-DSP |
|---|---|---|
| Methods compared | 8 + CVA, on a real palimpsest cube | 1 exact method + quarantined float foils |
| Scoring | **"determined visually, using colour pictures"** — no numeric score | integer counts, exhaustive where feasible |
| Operator dependence | thresholding foil *"depends on the human operator selecting suitable cutting values"* | no tunable thresholds on the exact path |
| Real multi-language corpus | **yes** — CRAM-DSP has not run on SGP | not yet |

**Honest position:** they have the broader empirical study on real data. The
differentiation is that their ranking cannot be reproduced by a third party from
the numbers, because there are no numbers.

---

## 4. Against generative recovery (PMR-GAN, Starynska et al.)

| Axis | Generative nets | CRAM-DSP |
|---|---|---|
| Visual quality of output | **high — state-of-the-art PSNR/SSIM** | no inpainting; nothing is invented |
| Ground truth | trained and scored against **synthesized** palimpsests | scored against planted ground truth and, on real data, against the artifact's own invariants |
| Hallucination risk | a model can emit letterforms never on the parchment | structurally impossible: every output is an exact function of input integers |
| Reversibility | none | bit-exact (P11) |
| Provenance | none | hash-chained receipts (P12) |

**Honest position:** for *restoration aesthetics* they win outright. For forensic
use the ranking inverts — a plausible letter that was never there is a false
positive of the worst kind, and PSNR against synthetic truth does not measure it.

---

## 5. Against classical forensic-imaging tooling

| Task | Classical | CRAM-DSP | Conditions |
|---|---|---|---|
| Copy-move detection | block DCT/PCA features, approximate matching (needed because float perturbs clones apart) | exact block hashing → dictionary lookup; IoU exact | Exact clones; a float pipeline forces the approximate approach |
| Requantization analysis | statistical estimators on compression artifacts | exact per-block gcd; background step estimated by divisibility | Integer-valued imagery |
| Splice localization | estimator-based, threshold-tuned | block IoU 20/20 on a deliberately misaligned mask; seam blocks self-flag | Synthetic, known truth |
| Edge/feature extraction | Sobel/Canny on float gradients | residue-lane class tests, no gradient formed | See scoping in `METRICS.md` §3 |

---

## 6. Against classical residue arithmetic (the substrate rivals)

| Axis | Classical RNS / literature | CRAM-DSP |
|---|---|---|
| Add / multiply | lane-parallel, carry-free — **identical** | identical (this is shared ground, not a claim) |
| Division & magnitude | `O(k²)` mixed-radix, or float interval evaluation (Isupov & Knyazkov 2021) | one modular subtract + one multiply (P1); subtraction alone on adjacent pairs (P3) |
| Floating point | present in the leading RNS division work | zero, statically linted |
| Reconstruction | Garner/MRC on the compute path | forbidden (A2); offline audit oracle only |
| Composite moduli | primality often assumed necessary | addressing layer needs coprimality only — witnessed exhaustively on (1800, 1001) |

---

## 7. Where comparators are ahead — recorded plainly

1. **Acquisition hardware.** The incumbent LED/sensor system has no counterpart here.
2. **A complete sealed scroll.** Vesuvius has read one; this framework has not.
3. **Breadth on real corpora.** Galen benchmarked nine methods on real folios;
   this framework's real-data record is one acquisition pass on Archimedes.
4. **Restoration output.** Generative models produce visually complete pages;
   this framework deliberately produces nothing that was not measured.
5. **Scale.** Teravoxel streaming pipelines exist; this engine is pure-Python and
   awaits its Rust/NEON port.

---

## 8. The uncontested axis

Across every comparator in this file, **not one reports a quantitative,
reproducible score.** Archimedes shipped on scholarly preference; Galen ranked by
eye; the GAN work scores against synthetic truth; Vesuvius names reproducibility
as an open problem. The hash-chained receipt and the bit-exact round trip answer a
question the field has documented as unanswered — which is why axis C is listed
first among the differentiators and why the Archimedes 14-bit lattice result
(`METRICS.md` §8) mattered on first contact: it is a property of the artifact that
the incumbent processing chain cannot see at all.
