# CRAM-DSP Baseline Dossier — Archimedes Palimpsest

Acquired 2026-08-19. Purpose: fix the incumbent baseline before CRAM-DSP touches the
artifact, on a target where the existing stack is documented to have **failed**.

---

## 1. Artifact acquired

Source: RIT mirror of the Archimedes Palimpsest data release
(`mirrors.rit.edu/archie/post-2007/HTML_TIFF/`), CC BY 3.0, original 16-bit rasters.
Full files are 8160 × 10880 × 3 × 16-bit = 532,690,516 bytes each, 15 bands per
folio. Acquired by parsing the remote TIFF IFD and issuing HTTP range requests for
exact row bands — no resampling, no transcoding: **the integers on disk are the
integers the camera wrote**.

| Window | Folio | Rows | Cols | Bands | Why |
|---|---|---|---|---|---|
| `archimedes_forgery.npz` | 081r-088v_Arch03r | 1700–2400 | 1600–4600 | 15 | **Inside the forged St. Mark painting** — where multispectral failed |
| `archimedes_control.npz` | 081r-088v_Arch03r | 6500–7200 | 1300–4300 | 15 | Ordinary palimpsest leaf, same bifolio — where multispectral succeeded |
| `archimedes_caltarget.npz` | 081r-088v_Arch03r | 1700–2400 | 7250–7950 | 15 | Reflectance/greyscale calibration target in the same frame |

Bands (all 15): LED365 (UV), LED445, LED470, LED505, LED530, LED570, LED617,
LED625 (visible), LED700, LED735, LED870 (IR), RAKBLL/RAKBLR (raking blue L/R),
RAKIRL/RAKIRR (raking IR L/R).

Capture metadata (from the per-band sidecars): 8160×10880, BitsPerSample 16,
SamplesPerPixel 3, uncompressed, 32.8 px/mm (833 ppi), leaf 247.65 × 330.2 mm,
imaged 2007-08-20 at the Walters Art Museum; creators Christens-Barry, Easton, Knox.

### First measurement — before any processing

An exhaustive `quant_fingerprint` pass over all 15 bands × 3 windows
(**70,350,000 sample values, 0 exceptions**) finds every value divisible by 4, with
per-band gcd exactly 4 and minimum step 4. The release is **14-bit sensor data
left-shifted into a 16-bit container**. Consequences: the true dynamic range is
0–16383, not 0–65535; any tool reporting 16-bit precision here is reporting two bits
of padding; and the KELD ladder should be run on v/4 (or on STAR16 with the lattice
declared) so band boundaries align to real quantization levels rather than to
padding. This came out of our own fingerprint statistic on first contact — it is the
kind of thing a float pipeline cannot see because normalization destroys the lattice
in the first operation.

---

## 2. Prior attempts on this exact target — and how they failed

The four forged Evangelist portraits (St. Mark f.081r, St. John f.057r,
St. Matthew f.064v, St. Luke) were painted onto the leaves in the 20th century in
gold leaf and pigment, directly over Archimedes text.

- **Multispectral imaging (2007 campaign, the stack described below): failed on these
  leaves.** The forgery pigment is opaque across the whole UV–NIR range the LED
  system covers; no band combination separates undertext from overpaint.
- **X-ray fluorescence at SLAC SSRL (2005–2006) succeeded** by imaging the iron in
  the ink rather than reflectance. The mirror's own manifest records XRF images for
  precisely these folios (081r, 057v-064r, 021v-028r, 001v, 144v-145r).
- Secondary documented failure modes on non-forgery leaves: mold damage (the imaging
  team's own papers note leaves where undertext is destroyed, not merely hidden),
  and the Alexander of Aphrodisias commentary leaves, where the standard pseudocolor
  rendering "improved little or not at all" and PCA on UV fluorescence had to be
  substituted.

**This is the baseline to beat: on the forgery window, the incumbent optical stack
recovers nothing and requires a synchrotron.**

---

## 3. Incumbent stack specs ("last stack")

The Easton / Knox / Christens-Barry system — still the field standard, adopted by the
Library of Congress, Oxyrhynchus, Dead Sea Scrolls, Sinai, and Galen projects.

| Layer | Specification |
|---|---|
| Illumination | LED narrowband, 13 bands 365–870 nm, Δλ ≤ 40 nm, + raking blue/IR from two sides |
| Sensor | 39 MP (Galen: 7216×5412) / Sinar 88 MP class here, 16-bit container, 14-bit data |
| Registration | spatial normalization across bands |
| Renderer 1 | **Pseudocolor (Knox)**: red-channel tungsten image → R; UV-blue image → G,B. Deterministic, no statistics |
| Renderer 2 | **"Sharpie"**: band subtraction, sharper undertext — with the acknowledged defect that subtraction *amplifies noise* |
| Renderer 3 | **PCA** on the band cube, plus supervised spectral-pseudoinverse segmentation and dynamical pseudocolor |
| Escalation | XRF (SSRL synchrotron) when optical fails |
| Evaluation | **visual judgement by scholars** — no quantitative metric, no reproducibility certificate |

Two structural weaknesses to measure against, both stated by the authors themselves:
subtraction amplifies noise, and method choice is per-leaf and operator-dependent
("the choice of technique is based on the preferences of the person trying to read
the manuscript").

---

## 4. Bleeding-edge comparators (the leaders, with their own numbers)

| Program | Method | Reported result | Where it's weak |
|---|---|---|---|
| **Vesuvius Challenge** (Seales/UKy + community) | ML ink detection on µCT + virtual unwrapping | First full scroll (PHerc. 1667) read end-to-end, June 2026; 300 TB/scroll ESRF scans; $2.14M prize pool open to June 2027 | Open problems posted July 2026 explicitly list "no ink vs no ink recovered yet" ambiguity and *workflow reproducibility at collection scale* |
| **Syriac Galen** (Manchester/Arsene et al., arXiv 1702.02508) | 8 dimensionality-reduction methods benchmarked: LDA, NCA, GDA, Isomap, Landmark Isomap, PPCA, PCA, GPLVM + CVA | Ranked in that order — **"determined visually"**; no numeric score reported | Success judged by eye; a hand-tuned double-thresholding foil depends on "the human operator selecting suitable cutting values" |
| **PMR-GAN** (Madi et al., IJDAR 26:211–222, 2023) | GAN over-text removal + inpainting | SOTA on **PSNR/SSIM** — trained on *synthesized* palimpsests | Metric is fidelity to a synthetic ground truth; hallucination risk on real undertext; not reversible, no provenance |
| **Starynska/Messinger/Kong** (IJDAR 24:181–195, 2021) | Generative text separation | Palimpsest separation with neural nets | Same class: irreversible, unverifiable output |
| **Codex Selden** (Snijders/Bodleian, JAS:Reports 2016) | Hyperspectral | Confirmed the hidden codex; ~7 of 20 pages | Cited in the Archimedes literature as a case where MSI effectiveness "was shown to be limited" |

**The measurable gap in the whole field: nobody reports a quantitative,
reproducible score.** Galen ranked eight methods *by eye*. Archimedes shipped on
scholarly preference. The GAN work reports PSNR/SSIM only against synthetic truth.
Vesuvius has named reproducibility as an unsolved problem in writing.

---

## 5. What this sets up

Three axes where CRAM-DSP can be scored against the incumbents on this exact data:

1. **The forgery window** — incumbent optical result: nothing (synchrotron required).
   Any residue-native separation above zero here is new ground.
2. **The control window** — head-to-head against pseudocolor / Sharpie / PCA on the
   same folio, with the calibration target in-frame giving exact reference values.
3. **Reproducibility** — the axis where no incumbent competes at all: the hash-chained
   receipt and the bit-exact round trip answer the question Vesuvius posted as open.

The noise-amplification defect the incumbents concede in subtraction, and the 14-bit
lattice they never declare, are both already measured above.
