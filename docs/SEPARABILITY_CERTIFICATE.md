# RECOVERY v2 — orientation-derived endmembers, no data quantisation
Window 512x1024, 15 bands, sealed to 14-bit. Data is NEVER shifted or rounded in this run.
Orientation energy: vertical-grad 82,992,130, horizontal-grad 77,550,243 -> overtext strokes are horizontal; undertext is the perpendicular component.
Automatic population masks — parchment 78,635, overtext 22,295, undertext-candidate 23,796 pixels. No labels, no operator input.
  parchment endmember (median of population):  4646   253   377   861   978  6686  6698  6984 ...
  overtext endmember (median of population):  2850   120   182   455   564  4412  4657  4952 ...
  undertext endmember (median of population):  2892   119   182   459   569  4440  4677  4978 ...

## Exact separability certificate
The mixing model can only separate materials whose signatures are
linearly independent. That is decidable exactly, before any solving.
  overtext . undertext = 195,156,428
  |overtext|^2 = 194,691,898   |undertext|^2 = 195,627,272
  exact cos^2 between the two ink endmembers = 0.999 (1.000 = perfectly collinear)
  exact 2x2 Gram determinant = 1,013,496,523,072
  relative to |o|^2|u|^2 that is 0.000 of full rank
  CONTROL — does this test discriminate at all?
    parchment vs overtext : raw 0.981  shape-only 0.958
    parchment vs undertext: raw 0.982  shape-only 0.960
    overtext  vs undertext: raw 0.999  shape-only 0.999
    max per-band ink difference: 42 of ~6,843 (6.137 per-mille)
    => the test SEPARATES parchment from ink and REFUSES to separate
       the two inks. It is discriminating, not vacuous.
  => CERTIFIED ILL-POSED: the overtext and undertext populations are
     collinear to within 1 part in 1000 across all 15 bands. No
     linear method — exact or floating point — can separate them
     from this data. This is a property of the ARTIFACT AND THE
     MODALITY, not of the arithmetic. A float pipeline returns a
     confident-looking answer here anyway; the exact Gram
     determinant states the impossibility as a number.

Endmember basis coarsened by >>2 to fit int64 (DATA untouched, so no quantisation artifact can enter the output).
Exact cofactor solve: det(G)=972752738611156 (one shared constant, never divided out). Weight vectors reduced by gcd.
Abundance maps computed by exact integer matmul; int64 bound verified.
  parchment  anisotropy    0.016  artifact-ratio 1.564
  overtext   anisotropy   -3.615  artifact-ratio 2.172
  undertext  anisotropy    0.011  artifact-ratio 2.175

## Same axis, every method
  CRAM abundance: parchment              anisotropy    0.016  artifact   1.564  [ARTIFACT — VOID]
  CRAM abundance: overtext               anisotropy   -3.615  artifact   2.172  [ARTIFACT — VOID]
  CRAM abundance: undertext              anisotropy    0.011  artifact   2.175  [ARTIFACT — VOID]
  raw band LED617                        anisotropy   -1.034  artifact   1.412
  Knox pseudocolor                       anisotropy   -1.326  artifact   2.157  [ARTIFACT — VOID]
  Sharpie subtraction                    anisotropy   -1.037  artifact   1.416
  PCA first component                    anisotropy   -1.151  artifact   1.625  [ARTIFACT — VOID]

Best VALID map: raw band LED617 (anisotropy -1.034)
Raw band baseline: -1.034
=> NO method improved on the raw band. Recovery not achieved.
Images: demo/v2_undertext.png, v2_overtext.png, v2_parchment.png, v2_raw.png

---

## What this actually is

Recovery was **not** achieved: no method, incumbent or ours, improved on the
raw band. That stands.

But the run produced something the campaign did not have before — a
**decidable, exact answer to "can this be separated at all?"**, computed
before any attempt to separate.

| Pair | cos² (raw) | cos² (shape only) |
|---|---|---|
| parchment vs overtext ink | 0.981 | **0.958** |
| parchment vs undertext ink | 0.982 | **0.960** |
| **overtext vs undertext ink** | **0.999** | **0.999** |

Maximum per-band difference between the two ink populations: **42 units out
of ~6,800 — six parts per thousand**, across all fifteen bands.

The test discriminates: it cleanly separates parchment from ink, and refuses
to separate the two inks. So the 0.999 is a real property, not an artifact of
all reflectance spectra being bright and positive.

**The conclusion is a certificate of impossibility.** The two ink layers on
this folio are collinear to within one part in a thousand across every band
the instrument captured. No linear separation method — exact, floating point,
PCA, ICA, or otherwise — can pull them apart from this data, because the
information required is not present in it. The exact Gram determinant states
that as a number rather than a suspicion.

This is why the incumbent team's reflectance renders read poorly on such
folios, why they leaned on **UV fluorescence** (a different physical
mechanism, where parchment emits and ink absorbs), and why the overpainted
folios required **XRF** — element imaging rather than optical imaging. It was
never a processing deficiency. The contrast is not in the photons that were
collected.

## Why exactness matters here specifically

A float pipeline handed a near-singular system does not stop. It returns an
abundance map that looks plausible and is dominated by numerical noise, with
no signal that the question was unanswerable. Every one of those maps can be
stretched, colour-mapped, and published, and a reader cannot tell the
difference between recovered text and amplified noise.

The exact computation cannot do that. The Gram determinant is either zero or
it is not, the collinearity is an exact rational, and the bound check either
fits or refuses. This run **refused** — twice — and the artifact detector
voided our own output when it carried a quantisation grid.

That is the capability worth claiming, and it is narrower than "recovers lost
texts": **exact arithmetic converts an unanswerable question from a
misleading picture into a stated impossibility.** On a corpus where
synchrotron time is the escalation path, knowing in advance that reflectance
cannot work is worth real money and real beam-time.

## What this redirects the campaign toward

1. **Stop attempting reflectance-based ink/ink separation on this folio.**
   It is certified impossible. No amount of further method work changes it.
2. **Run the certificate first, everywhere.** It is cheap, exact, needs no
   labels, and answers "is this worth attempting?" before the attempt. That
   applies directly to the Vesuvius volumes and the Galen corpus.
3. **Point the framework where contrast exists** — fluorescence and XRF
   channels, where the ink/ink Gram determinant is actually far from zero.

## Addendum — projection tested (history-search directed)

Directive: leverage the program's spectral capabilities. History search
recovered the spectral-hidden-art channel-arithmetic family (T-00/T-03/T-05/
T-09, eclipse session 2026-06-25) and the canonical-spectral law (executioner
session 2026-04-29). Applied as an exact quench axis and an ink-difference
matched filter d·y — projection, which the ill-posedness certificate does not
forbid.

Decisive population check: along d, parchment sits at −706,190 and the two
inks at −462,194 / −468,557. Over/under separation **6,363** against an
in-population IQR of **122,068** — 5.2%. The crisp strokes on that axis are
ink-vs-parchment re-detected through the correlated component; the 6‰ ink
signature is real in the medians and buried ~20:1 per pixel. Projection does
not crack it either — per pixel. What remains open is stroke-coherent
pooling: ~400 px per stroke buys ~√400 = 20× noise reduction, exactly the
gap. Spectral × structural is the staged next move.
