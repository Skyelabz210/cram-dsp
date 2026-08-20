# RECOVERY RUN — Archimedes control window

Window: rows 100-612, cols 400-1424, 15 bands, sealed to 14-bit. 524,288 pixels.
Raw LED617 orientation energy: vertical-gradient 82,992,130, horizontal-gradient 77,550,243
Dominant (overtext) stroke direction reads as: horizontal strokes. Undertext is therefore the perpendicular component.
Baseline (raw band) undertext-orientation ratio: -1.034

## Exact endmember extraction
Selected 3 endmembers by exact greedy residual search (deterministic, no float, no random seed).
  E0:  4139   283   431   973  1143  8628  8160  7818 ...
  E1:  3927    68   103   231   302  2347  2577  2911 ...
  E2:  2824    98   154   401   534  4300  4493  5053 ...

## Exact unmixing
Abundance maps computed for all 524,288 pixels via one integer matmul against the exactly-inverted pseudoinverse.
Basis quantised by >>4 so the exact solve provably fits int64; common denominator D=726358658058155. Exactness is with respect to this basis.
Pixels EXACTLY explained by the 4-endmember model (residual identically zero): 3 / 524,288 (0.000%)
A float pipeline cannot make that statement about any pixel — it can only report a small residual and threshold it.

## Scoring every abundance map on the orientation axis
  endmember E0 abundance: undertext-orientation ratio 1.003
  endmember E1 abundance: undertext-orientation ratio 0.159
  endmember E2 abundance: undertext-orientation ratio 0.755
=> E0 carries the strongest perpendicular (undertext) signature.

## Head-to-head against the incumbent renders, same window, same axis
  raw band LED617                               -1.034
  incumbent: Knox pseudocolor                   -1.326
  incumbent: Sharpie subtraction                -1.037
  incumbent: PCA first component                -1.151
  CRAM exact unmixing (undertext abundance)     1.003

## Artifact check (a score is void if the map is not an image)
  CRAM exact unmixing: mean |checkerboard-phase difference| 111896649494941, mean |adjacent difference| 52302718325138
  => HIGH-FREQUENCY PHASE ARTIFACT DETECTED. The map carries a grid pattern from basis quantisation, not manuscript structure. Its directional score is VOID.

## VERDICT
RECOVERY NOT ACHIEVED. The exact-unmixing map is disqualified by its own artifact check, so its score does not count. Among the maps that remain valid, no method separates undertext on this window: every incumbent render and the raw band score negative on the undertext orientation axis, meaning the dominant stroke direction still dominates after processing.

Two distinct causes, both real:
  1. MODEL. Greedy vertex endmember extraction selects extremal pixels, which on noisy sensor data are outliers, not materials. Nothing downstream can fix a basis that does not correspond to parchment / overtext ink / undertext ink.
  2. NUMERICS. Fitting the exact rational solve into int64 required quantising the basis by >>4, and that quantisation is what stamped the grid pattern into the output. Exactness was preserved with respect to the quantised basis, and the quantised basis was wrong.

Neither cause is arithmetic precision. Exact arithmetic cannot resolve an ill-posed separation: if the endmembers are wrong, the exact answer to the wrong question is still wrong.

Images written to demo/: recover_raw, recover_knox, recover_sharpie, recover_pca, recover_cram_undertext, recover_abundance_E0..E3.

---

## What would actually complete the task

The task is: make the erased writing readable. Not preserve it, not certify
it, not process it reversibly — **read it**. This attempt did not.

### Why exactness did not deliver recovery

Separation is a modelling problem, not a precision problem. The mixing model
`Y = M a` can be solved exactly, and this repo now does solve it exactly —
but the solution is only meaningful if `M` holds the true material
signatures. Choosing `M` by unsupervised extremal search puts sensor
outliers in the basis, and an exact solve against a wrong basis returns an
exactly wrong answer. That is the whole result, stated plainly.

There is a second, physical reason specific to this manuscript: the
Archimedes undertext and the Euchologion overtext are **both iron-gall ink**.
Two chemically similar inks have similar reflectance spectra, so no amount
of arithmetic separates them from reflectance data alone. This is precisely
why the incumbent team relied on **UV fluorescence** (different physics:
parchment fluoresces, ink absorbs the excitation) rather than reflectance
band math, and why the overpainted folios needed **XRF** — element imaging,
not optical imaging.

### The three things that would complete it

1. **Correct endmembers.** Verified pure-pixel labels for parchment,
   overtext ink, undertext ink, and damage — a few dozen boxes, human
   verified. This is NODE-ARC03, previously filed as a HUMAN-VERIFY gate.
   It is not bureaucracy: **it is the actual bottleneck.** With a correct
   basis the exact solve becomes valuable in a way no float method can
   match — per pixel it returns an exact rational abundance and an exact
   residual, so "this pixel contains undertext ink" becomes a decision with
   a certificate rather than a thresholded score.
2. **A modality with real contrast between the two inks.** Reflectance under
   narrowband LEDs is the wrong instrument for two iron-gall inks. UV
   fluorescence, or XRF for the overpainted folios, is where the contrast
   physically exists. No processing layer substitutes for absent contrast.
3. **The orientation prior, used as a constraint rather than a score.** The
   undertext runs perpendicular to the overtext. That is strong, free,
   physically-grounded structure. Used as a separation constraint — not
   merely as the evaluation axis it served as here — it is independent of
   ink chemistry and survives spectral similarity.

### Honest position of the framework

What CRAM-DSP has proven: the arithmetic is exact, the transforms are
reversible, the pipeline is reproducible by hash, the artifact's true bit
depth was recovered on first contact, and evidence survives processing that
destroys it under float. All measured, all reproducible.

What it has **not** proven: that any of that reads a word of Archimedes.
Until it does, the correct description of this work is an exact substrate
with a verified provenance layer — not a recovery method. The boards stay
open and the negatives stay published.
