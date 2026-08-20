# Archimedes Run — Objective Results

**75,564,310 exact checks — 0 failures.**

## A — Acquisition and lattice (NODE-INF04 seam, receipted)
  control: lattice step 4, effective bits 14, raw range [6980,37044] -> sealed [1745,9261]
  forgery: lattice step 4, effective bits 14, raw range [1836,65532] -> sealed [459,16383]
  caltarget: lattice step 4, effective bits 14, raw range [928,38892] -> sealed [232,9723]
  exhaustive: 70,350,000 sample values, 0 not on the step-4 lattice => published 16-bit release carries 14-bit sensor data (2 bits padding)

## B — NODE-ARC02: band registration audit (exact integer, no resampling)
  LED365: best integer shift (dy,dx)=(0, 0), runner-up worse by 0.720%
  LED445: best integer shift (dy,dx)=(1, 0), runner-up worse by 0.011%
  LED470: best integer shift (dy,dx)=(0, 0), runner-up worse by 0.014%
  LED505: best integer shift (dy,dx)=(0, 0), runner-up worse by 0.094%
  LED530: best integer shift (dy,dx)=(0, 0), runner-up worse by 0.240%
  LED570: best integer shift (dy,dx)=(0, 0), runner-up worse by 32.602%
  LED617: best integer shift (dy,dx)=(0, 0), runner-up worse by 3782263200.000%
  LED625: best integer shift (dy,dx)=(0, 0), runner-up worse by 52.501%
  LED700: best integer shift (dy,dx)=(0, 0), runner-up worse by 5.873%
  LED735: best integer shift (dy,dx)=(0, 0), runner-up worse by 1.545%
  LED870: best integer shift (dy,dx)=(0, -1), runner-up worse by 0.301%
  RAKBLL: best integer shift (dy,dx)=(1, 0), runner-up worse by 0.008%
  RAKBLR: best integer shift (dy,dx)=(0, 0), runner-up worse by 0.002%
  RAKIRL: best integer shift (dy,dx)=(6, 0), runner-up worse by 0.019%
  RAKIRR: best integer shift (dy,dx)=(-6, -2), runner-up worse by 0.015%
  bands off-reference: 5/15 (LED445, LED870, RAKBLL, RAKIRL, RAKIRR). DECLARED, not corrected: A1 forbids resampling evidence to hide misalignment.

## C — NODE-INF02: lane sizing against REAL band deltas (P6)
  observed |delta| range on sealed control band: 0..1,930
  lanes (7, 11, 13): value-exact to |d|<=500  -> ALIASES — unusable here
  lanes (11, 13, 17, 19): value-exact to |d|<=23,094  -> COVERS
  lanes (7, 11, 13, 17, 19): value-exact to |d|<=161,661  -> COVERS
  real pixels whose delta exceeds the 8-bit comb's period (1001): 1,318 — each would be misread as delta mod 1001 by the 8-bit lane set. This is why the S8 extenders {17,19} are load-bearing on real 14-bit evidence, not decorative.

## D — Reversibility and reproducibility on real 14-bit evidence
  524,288 real sensor values through forward+inverse: zero changed
  chain head: 9452753f37e6939c8d4c6cb0a0c647a3...

## E — NODE-ARC07: survivability head-to-head, control window
  Axis E. No human labels needed: the question is what each pipeline
  destroys, measured against the artifact's own structure.
  CRAM reversible round trip:
     source lattice preserved on 100.000% of values | distinct levels 5,085 (was 5,085) | unit-step evidence 2,513 (was 2,513)
  incumbent: float blur+round (sigma=1):
     source lattice preserved on 25.136% of values | distinct levels 17,226 (was 5,085) | unit-step evidence 1,182 (was 2,513)
  incumbent: Sharpie band subtraction:
     source lattice preserved on 100.000% of values | distinct levels 4,884 (was 5,085) | unit-step evidence 2,606 (was 2,513)
  (fingerprint-block count is 2048/2048 for every path: on continuous-tone sensor data every block has a nonzero gcd, so that statistic does not discriminate here. It discriminates on synthetic requantised evidence, T9. Reported so the null is on the record.)
  Sharpie preserves the lattice exactly — subtraction of two step-4 values stays on step 4 — so the incumbent WINS this axis against float blur. Its cost shows in the last column instead: unit-step evidence rises above the source count, which is the noise amplification its own authors concede.

## F — NODE-ARC09: forgery window characterization (Board 1)
  Incumbent optical baseline on these folios: recovers nothing;
  the project escalated to synchrotron XRF. This run is
  CHARACTERIZATION, not a recovery claim. No XRF reference is on
  disk (NODE-ARC08 unresolved), so nothing here is corroborated.
  forgery window: lattice step 4, effective bits 14, range [459,16383]
  darkest-quintile (paint-dominated) pixels: 419,917; brightest quintile (substrate): 419,961
  LED365 (UV): under-paint spread 3,834 (mean 1178.741), substrate spread 6,251 (mean 3138.459)
  LED617 (red): under-paint spread 1,787 (mean 1341.840), substrate spread 10,483 (mean 7201.881)
  LED870 (IR): under-paint spread 5,397 (mean 1888.377), substrate spread 14,182 (mean 7518.253)
  lane 11 class-occupancy deviation from uniform: under paint 0.004%, substrate 0.005%
  lane 13 class-occupancy deviation from uniform: under paint 0.004%, substrate 0.006%
  unit-step probe fires: 2,865 under paint, 456 on substrate
  VERDICT (Board 1): the residue-native probes run and return exact,
  reproducible statistics under the overpaint, but this run produces NO
  legible-undertext claim. Reported as a shipped negative on the
  recovery axis, per BENCHMARKS.md rule 3. Corroboration via XRF
  (NODE-ARC08) remains the gate for any positive claim here.
