# Archaeological & Heritage Imaging Reference (dsp-analyst)

Collected 2026-08-19. The modality catalog, the incumbent processing stacks
with their own conceded limits, the digitization-quality standards, and
per-corpus notes for the program's target artifacts.

## 1. Modality catalog (what to reach for, when)

| Modality | Physics | Best for | Analyst cautions |
|---|---|---|---|
| **Multispectral (MSI)** | 10–15 narrowband LED reflectance/fluorescence, UV→NIR | Erased/overwritten ink, palimpsests | Field standard (see §2); fails on opaque overlayers; evaluation is traditionally visual |
| **Hyperspectral (HSI)** | Contiguous spectral cube | Pigment discrimination, hidden layers (Selden) | Data volume; calibration; still reflectance-bound |
| **XRF mapping** | Element fluorescence (Fe, Ca, Cu…) | Ink under paint/gold; iron-gall under anything optical fails on | Synchrotron access for large scans; element ≠ text without spatial care |
| **IR reflectography** | NIR penetration of paint layers | Underdrawings, carbon layers | Depth/contrast depends on pigment IR transparency |
| **UV fluorescence** | Organic response | Erasures, retouch, varnish | Surface-only; dyes confound |
| **RTI / H-RTI (PTM)** | Many known/recovered light directions → per-pixel reflectance model | Incised/embossed text, tool marks, use-wear, rock engravings — relightable; roots in raking light | Not spectral; highlight method recovers light from a reflective sphere; microscopic-RTI extends to sub-mm use-wear |
| **DStretch (decorrelation stretch)** | Color-space decorrelation | Faint pictographs/rock-art pigment | An *enhancement*, not a measurement — hue transforms mislead if read literally; pair with untouched record |
| **Photogrammetry / SfM** | Multi-view 3-D | Surfaces, petroglyphs, sites; measurable models | Non-contact is the modern standard for rock art; scale control; SWGDE governs forensic measurement uses |
| **µCT + virtual unwrapping** | X-ray density volume | Sealed/carbonized scrolls (Herculaneum, En-Gedi) | Carbon ink ≈ papyrus density: the ink-detection problem; teravoxel scale |
| **OCT** | Optical coherence depth profiles | Varnish/layer stratigraphy | Small fields |
| **Raking light** | Low-angle illumination | Surface topology, erasure scars | The RAK bands in the Archimedes set are exactly this |

Escalation ladder for text recovery: standard MSI → band algebra/statistics →
fluorescence variants → XRF (element imaging) → phase/higher-energy methods.
The Archimedes forgery folios are the canonical example: optical MSI recovered
nothing; SLAC synchrotron XRF read the iron ink under the paint.

## 2. The incumbent manuscript stack (and its own concessions)

Easton / Knox / Christens-Barry system (Archimedes team; standardized 2010;
adopted by LoC, Sinai, Galen, DSS projects): 13 LED bands 365–870 nm
(Δλ ≤ 40 nm) + raking blue/IR; registration; then three renderers —
deterministic **pseudocolor** (tungsten-red → R, UV-blue → G,B), **"Sharpie"
subtraction**, and **PCA** — with XRF escalation and *visual* evaluation.

Conceded weaknesses (their publications): subtraction *amplifies noise*;
method choice is per-leaf operator preference; on some leaves pseudocolor
"improved little or not at all" and PCA-on-fluorescence had to substitute.

Field-wide evaluation gap (documented in this repo's PRIOR_ART.md): Galen
ranked eight dimensionality-reduction methods **visually** with no numeric
score; GAN restoration reports PSNR/SSIM against synthetic truth (with
structural hallucination risk); Vesuvius lists reproducibility as an open
problem. **Quantitative, reproducible scoring is the empty axis.**

## 3. Digitization-quality standards (speak this vocabulary)

- **FADGI** Technical Guidelines for Digitizing Cultural Heritage Materials,
  3rd ed. (2023): the four-star system; 3rd edition aligns its evaluation
  parameters to **ISO 19264-1:2021** and moves measurements to L\*a\*b\*;
  conformance is demonstrated with targets + analysis software (DICE-style),
  not claimed. Star level is chosen per material class and use, not maxed
  blindly.
- **ISO 19264-1** (Photography — Archiving systems — Image quality analysis,
  reflective originals): the international method — defined metrics with
  aims/tolerances, tiered levels (A/B/C). Companion vocabulary ISO 19262 and
  best-practice TR 19263-1.
- **Metamorfoze** (Netherlands): three tiers (Strict / Light / Extra Light);
  founding principle that masters must be faithful enough to *replace*
  originals.
- Analyst uses: (a) read capture metadata against these expectations;
  (b) when characterizing acquired data, report resolution, bit depth
  (measured, not nominal — cf. the 14-bit lattice), illumination, and
  targets present; (c) never claim archival-grade language for data that
  hasn't been conformance-tested.
- Related plumbing worth naming in reports: IIIF for dissemination;
  TIFF/JPEG2000-lossless masters; embedded calibration targets as in-frame
  ground truth (the Archimedes caltarget window is exactly this).

## 4. Per-corpus notes (program targets)

- **Archimedes Palimpsest** (CC BY, RIT mirror): 15 bands/folio, 8160×10880
  ×3×16-bit rasters; measured value lattice gcd 4 ⇒ 14-bit sensor data in a
  16-bit container (70,350,000 values, 0 exceptions) — align KELD to v/4 and
  use 14-bit lane sets. Forged Evangelist folios = documented optical
  failure, XRF success; mirror carries XRF assets for 081r et al.
- **Syriac Galen Palimpsest** (CC BY, digitalgalen.net / OPenn 0014): full
  raw MSI + XRF sets; illegible regions persisted after 100 MP MSI; the
  eight-method benchmark was ranked visually — first numeric score is open.
- **Vesuvius / Herculaneum**: OME-Zarr open volumes (S3), ink/surface label
  sets (2026-07), tifxyz meshes, VC3D; reproducibility and
  "no ink vs no ink recovered yet" posted as open problems; prizes per the
  repo's BOUNTIES.md.
- **Codex Selden (Añute)**: hidden pre-colonial codex under gesso; ~7 of 20
  pages hyperspectrally probed (2016); cubes not openly posted — outreach
  target; Digital Bodleian RGB available for characterization only.
- **Sinai Palimpsests**: 74 mss / 6,800 pp spectral, 305 undertexts;
  registered scholarly access (UCLA).
- **Dresden Codex**: SLUB scans; program-internal blockers P75–P78 identity,
  P54–56, repair seams, tonal-window layer; evidence law in the
  archeoastronomy-codex skill.

## 5. Enhancement ethics (heritage edition)

- Keep the untouched master inseparable from any enhanced derivative;
  publish the transform, not just its output (reversible transforms with
  receipts satisfy this maximally).
- DStretch-class false color and pseudocolor are *interpretive aids*;
  conclusions drawn from them need corroboration in measured values.
- Generative restoration is presentation, never evidence; label it as such
  everywhere it appears.
- Non-contact methods are the modern standard for fragile surfaces (rock
  art tracing by hand is obsolete); imaging campaigns should record
  capture geometry for reproducibility (RTI's Digital-Lab-Notebook culture
  is the model).
