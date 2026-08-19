# PRIOR ART

What exists, who built it, what it achieves, and — stated in their own words where
possible — where it stops. This file is the reference frame; `COMPARISONS.md` is
the head-to-head.

---

## 1. The incumbent manuscript-imaging stack

**Easton / Knox / Christens-Barry system** (Archimedes Palimpsest imaging team,
1998–2008; standardized 2010). Adopted since by the Library of Congress, the
Oxyrhynchus papyri, the Dead Sea Scrolls, Sinai Palimpsests, and the Syriac Galen
Palimpsest. This is the field standard.

| Layer | Specification |
|---|---|
| Illumination | LED narrowband, 13 bands 365–870 nm, Δλ ≤ 40 nm; raking blue and IR from two sides |
| Capture | high-resolution monochrome + colour sensors; 16-bit container; fluorescence imaging supported |
| Registration | spatial normalization across bands |
| Renderer 1 | **Pseudocolor (Knox)** — red-channel tungsten image → R; UV-blue → G and B. Deterministic |
| Renderer 2 | **"Sharpie"** — band subtraction; sharper undertext, named for Robert Sharples |
| Renderer 3 | **PCA** on the band cube; also supervised spectral-pseudoinverse segmentation and dynamical pseudocolor rendering |
| Escalation | **XRF** (SSRL synchrotron) when optical methods fail |
| Evaluation | scholarly visual judgement |

**Conceded limitations, from the authors' own publications:**

- Subtraction (the Sharpie path) *"also enhances any noise in the images, which
  may interfere with the reading of the text."*
- Method choice is per-leaf and operator-dependent. On the Alexander of
  Aphrodisias leaves the standard pseudocolor rendering *"improved little or not
  at all"*, and PCA on UV-fluorescence colour images had to be substituted.
- No quantitative metric is reported anywhere in the pipeline; success is
  established by scholars finding the output readable.

**References.** Easton, Knox, Christens-Barry, Boydston, Toth, Emery, Noel,
"Standardized system for multispectral imaging of palimpsests," *Computer Vision
and Image Analysis of Art*, SPIE 7531 (2010) 75310D. Easton, Christens-Barry,
Knox, "Spectral image processing and analysis of the Archimedes Palimpsest,"
EUSIPCO 2011, 1440–1444.

---

## 2. Documented failure on the target artifact

Folios bearing the four forged Evangelist portraits — St. Mark f.081r, St. John
f.057r, St. Matthew f.064v, St. Luke — were overpainted in the 20th century in
gold leaf and pigment directly over Archimedes text.

- **Optical multispectral failed on these leaves.** The forgery pigment is opaque
  across the entire UV–NIR range the LED system covers; no band combination
  separates undertext from overpaint.
- **XRF at SLAC SSRL (2005–2006) succeeded**, imaging the iron in the ink rather
  than reflectance. The data release manifest records XRF images for exactly
  these folios (081r; 057v–064r; 021v–028r; 001v; 144v–145r).
- Additional documented failure mode on other leaves: mold damage, where
  undertext is destroyed rather than hidden.

This is the baseline condition for the acquired `forgery` window: **incumbent
optical recovery is zero, and a synchrotron is the escalation path.**

---

## 3. Comparator programs at the frontier

### Vesuvius Challenge (Seales / University of Kentucky + open community)
Virtual unwrapping of carbonized Herculaneum scrolls from micro-CT, with ML ink
detection. PHerc. 1667 was virtually unwrapped and read end-to-end (announced
June 2026) — the first complete scroll. Scans reach ~300 TB per scroll at ESRF;
open data in S3 as cloud-optimized OME-Zarr; $2.14M prize pool open to the
June 2027 Grand Prize deadline; 600+ scrolls still unread.

*Where it stops (their own July 2026 open-problems posting):* distinguishing
"no ink" from "no ink recovered yet"; reducing dependence on approximate labels;
inferring surfaces without months of correction; and **making the workflow
reproducible enough for collection-scale reading**.

### Syriac Galen Palimpsest (Manchester — Arsene, Pormann, Sellers, Bhayro)
Benchmarked eight dimensionality-reduction methods on the SGP multispectral cube:
supervised GDA, LDA, NCA; unsupervised GPLVM, Isomap, Landmark Isomap, PCA, PPCA;
compared against Canonical Variates Analysis.

*Where it stops:* the ranking (LDA, NCA, GDA, Isomap, Landmark Isomap, PPCA, PCA,
GPLVM) was **"determined visually, using colour pictures"** — no numeric score is
reported. Their hand-tuned double-thresholding foil explicitly *"depends on the
human operator selecting suitable cutting values."* Even after 100 MP
multispectral capture, illegible regions remained large enough that establishing
connected text proved impossible, forcing synchrotron XRF.
*Reference:* arXiv:1702.02508.

### Generative / neural palimpsest recovery
- **PMR-GAN** (Madi, Alaasam, Shammas, El-Sana, *IJDAR* 26:211–222, 2023):
  over-text removal plus inpainting; reports state-of-the-art **PSNR/SSIM** —
  trained on *synthesized* palimpsests.
- **Starynska, Messinger, Kong** (*IJDAR* 24:181–195, 2021): palimpsest text
  separation with generative networks.

*Where they stop:* the metric measures fidelity to a synthetic ground truth, not
recovery of a real undertext; the mapping is irreversible; and a generative model
can produce plausible letterforms that were never on the parchment — a
disqualifying property for forensic use, where the question is what the artifact
*contains*, not what a model finds likely.

### Codex Selden / Añute (Snijders, Bodleian + Leiden/Delft, *JAS: Reports* 2016)
Hyperspectral imaging confirmed a hidden pre-colonial Mixtec codex beneath gesso;
roughly 7 of 20 pages scanned before time ran out. Cited within the Archimedes
literature as a case where multispectral effectiveness *"was shown to be limited."*

### Sinai Palimpsests Project (EMEL / St Catherine's / UCLA)
74 palimpsests, 6,800 pages, 305 erased texts identified — the largest spectral
dataset in the humanities. Of 160+ known Sinai palimpsests, only a minority have
confidently identified undertexts.

---

## 4. Residue-arithmetic prior art (the substrate side)

From the program's own December 2025 survey and subsequent audits:

- **Classical RNS.** Lane-parallel add/multiply; division, comparison, sign, and
  magnitude require reconstruction or mixed-radix conversion — `O(k²)` sequential
  steps. Standard references treat RNS division as an open difficulty.
- **Isupov & Knyazkov** (MDPI, 2021), "High-Performance Computation in RNS Using
  Floating-Point Arithmetic": handles cryptographic-scale dynamic ranges but
  relies on **floating-point interval evaluation** for division, stating plainly
  that division in RNS remains hard to implement.
- **Garner (1959) / mixed-radix conversion:** fuses CRT lanes into one positional
  magnitude — a non-native operation that steps outside the product ring, emits
  values that are functions of all previously visited lanes, and destroys residue
  i.i.d. Forbidden here by A2; permitted only as an offline audit oracle.
- **End-to-end RNS design** is recommended by the cryptographic community (one
  input conversion, one output conversion) — the same posture A2 formalizes.

**The gap this framework occupies:** exact integer division and winding recovery
in residue space with no floating point and no reconstruction (P1–P3, P5), applied
as a signal-processing substrate rather than a cryptographic one.

---

## 5. Standard forensic-imaging prior art (the forensics side)

- **Copy-move detection** conventionally uses block DCT/PCA features with
  approximate matching, because float pipelines perturb clones apart.
- **Requantization / JPEG-ghost analysis** infers processing history from
  compression artifacts; typically statistical and estimator-based.
- **Reversible watermarking and lossless colour transforms** (JPEG2000 RCT,
  LeGall 5/3 lifting) are established, standardized, and reused here directly —
  cited, not reinvented (P11).
- **Reversible integer KLT** (Hao & Shi, *IEEE TSP* 2001) and integer-to-integer
  wavelets (Calderbank, Daubechies, Sweldens, Yeo) exist; a *full data-adaptive*
  integer RKLT for multispectral manuscript separation is not standard practice
  and remains queued as future work here.

---

## 6. What no one in the field reports

Across every comparator above: **no quantitative, reproducible score.** Archimedes
shipped on scholarly preference. Galen ranked eight methods by eye. The GAN work
reports PSNR/SSIM against synthetic truth. Vesuvius has named reproducibility as
an unsolved problem in writing.

That absence defines the axis in `METRICS.md`.
