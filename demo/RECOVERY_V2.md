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
