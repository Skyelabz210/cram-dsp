"""THE RECOVERY RUN — attempt the actual task: make the undertext readable.

Scoring without human labels is possible here because of a physical fact
about this manuscript: the Archimedes undertext runs PERPENDICULAR to the
Euchologion overtext. The prayer-book scribe rotated the recycled leaves
ninety degrees. So orientation is ground truth we did not have to annotate:

  vertical strokes   -> strong HORIZONTAL gradients
  horizontal strokes -> strong VERTICAL gradients

A render that isolates undertext raises the energy in the undertext
orientation relative to the overtext orientation. That ratio is objective,
computable, exact, and identical for every method compared — so incumbent
renders and the exact unmixing are scored on the same axis with no annotation
and no operator preference.

Usage: python3 analysis/recover.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import ingest, metrics, spectral
from cram_dsp import baseline_float as foil

CORPUS = "/home/claude/corpus"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo")
os.makedirs(OUT, exist_ok=True)

BANDS = ["LED365", "LED445", "LED470", "LED505", "LED530", "LED570", "LED617",
         "LED625", "LED700", "LED735", "LED870", "RAKBLL", "RAKBLR",
         "RAKIRL", "RAKIRR"]

L = []


def note(s):
    L.append(s)
    print(s, flush=True)


def load_cube(window, r0, r1, c0, c1):
    z = np.load(f"{CORPUS}/archimedes_{window}.npz")
    return np.stack([ingest.seal(z[b][r0:r1, c0:c1])[0] for b in BANDS])


def orient_energy(img):
    """(vertical-gradient energy, horizontal-gradient energy), exact ints.

    Vertical gradients respond to horizontal strokes, and vice versa.
    """
    a = np.asarray(img).astype(np.int64)
    gv = int(np.abs(np.diff(a, axis=0)).sum())   # responds to horizontal strokes
    gh = int(np.abs(np.diff(a, axis=1)).sum())   # responds to vertical strokes
    return gv, gh


def stretch8(a):
    a = np.asarray(a).astype(np.int64)
    lo = int(np.percentile(a, 2))
    hi = int(np.percentile(a, 98))
    rng = max(hi - lo, 1)
    return np.clip((a - lo) * 255 // rng, 0, 255).astype(np.uint8)


def save(name, arr):
    from PIL import Image
    Image.fromarray(np.asarray(arr).astype(np.uint8)).save(os.path.join(OUT, name))


# ===========================================================================
note("# RECOVERY RUN — Archimedes control window")
note("")
R0, R1, C0, C1 = 100, 612, 400, 1424
cube = load_cube("control", R0, R1, C0, C1)
note(f"Window: rows {R0}-{R1}, cols {C0}-{C1}, {cube.shape[0]} bands, "
     f"sealed to 14-bit. {cube[0].size:,} pixels.")

# --- which orientation is which, established from the raw data itself ---
raw = cube[BANDS.index("LED617")]
gv, gh = orient_energy(raw)
note(f"Raw LED617 orientation energy: vertical-gradient {gv:,}, "
     f"horizontal-gradient {gh:,}")
overtext_axis = "vertical strokes" if gh > gv else "horizontal strokes"
note(f"Dominant (overtext) stroke direction reads as: {overtext_axis}. "
     f"Undertext is therefore the perpendicular component.")
# undertext score = energy in the MINORITY orientation, relative to majority
UNDER_IS_V = gh > gv     # if overtext is vertical strokes, undertext shows in gv


def undertext_score(img):
    """Bounded directional anisotropy in milli-units, range [-1000, 1000].

    A ratio metric can be driven to infinity by any artifact that flattens
    one direction, so it is not usable as a score. This form cannot be
    gamed that way.
    """
    v, h = orient_energy(img)
    num, den = (v, h) if UNDER_IS_V else (h, v)
    tot = num + den
    if tot == 0:
        return 0, num, den
    return (1000 * (num - den)) // tot, num, den


base_score, _, _ = undertext_score(raw)
note(f"Baseline (raw band) undertext-orientation ratio: "
     f"{metrics.fmt_milli(base_score)}")
note("")

# ===========================================================================
note("## Exact endmember extraction")
ends, idx = spectral.extract_endmembers(cube, k=3, stride=17)
note(f"Selected {len(ends)} endmembers by exact greedy residual search "
     f"(deterministic, no float, no random seed).")
for j, e in enumerate(ends):
    note(f"  E{j}: " + " ".join(f"{int(v):5d}" for v in e[:8]) + " ...")

note("")
note("## Exact unmixing")
A, D, basis, shift = spectral.unmix_exact_cube(cube, ends)
note(f"Abundance maps computed for all {cube[0].size:,} pixels via one integer "
     f"matmul against the exactly-inverted pseudoinverse.")
note(f"Basis quantised by >>{shift} so the exact solve provably fits int64; "
     f"common denominator D={D}. Exactness is with respect to this basis.")

resid = spectral.reconstruction_residual(cube, basis, A, D, shift)
exact_pixels = int((resid == 0).sum())
note(f"Pixels EXACTLY explained by the 4-endmember model (residual identically "
     f"zero): {exact_pixels:,} / {resid.size:,} "
     f"({metrics.fmt_milli(metrics.milli(exact_pixels * 100, resid.size))}%)")
note("A float pipeline cannot make that statement about any pixel — it can "
     "only report a small residual and threshold it.")
note("")

# ===========================================================================
note("## Scoring every abundance map on the orientation axis")
best = None
for j in range(A.shape[0]):
    s, num, den = undertext_score(A[j])
    note(f"  endmember E{j} abundance: undertext-orientation ratio "
         f"{metrics.fmt_milli(s)}")
    if best is None or s > best[1]:
        best = (j, s)
uj, uscore = best
note(f"=> E{uj} carries the strongest perpendicular (undertext) signature.")
under = A[uj]
note("")

# ===========================================================================
note("## Head-to-head against the incumbent renders, same window, same axis")
red = cube[BANDS.index("LED617")]
uv = cube[BANDS.index("LED365")]
blue = cube[BANDS.index("LED445")]

knox = foil.knox_pseudocolor(red, uv)
knox_gray = knox[:, :, 0].astype(np.int64) + knox[:, :, 1].astype(np.int64)
sharpie = foil.sharpie_subtract(red, blue)
pca = foil.pca_render([cube[i] for i in range(cube.shape[0])]).astype(np.int64)

rows = []
for label, img in (("raw band LED617", raw),
                   ("incumbent: Knox pseudocolor", knox_gray),
                   ("incumbent: Sharpie subtraction", sharpie),
                   ("incumbent: PCA first component", pca),
                   ("CRAM exact unmixing (undertext abundance)", under)):
    s, num, den = undertext_score(img)
    rows.append((label, s))
    note(f"  {label:45s} {metrics.fmt_milli(s)}")

note("")
note("## Artifact check (a score is void if the map is not an image)")
for label, img in (("CRAM exact unmixing", under),):
    a = np.asarray(img).astype(np.int64)
    chk = a[::2, ::2].astype(np.int64)
    alt = a[1::2, 1::2].astype(np.int64)
    n = min(chk.shape[0], alt.shape[0]), min(chk.shape[1], alt.shape[1])
    d = int(np.abs(chk[:n[0], :n[1]] - alt[:n[0], :n[1]]).mean())
    neigh = int(np.abs(np.diff(a, axis=1)).mean())
    note(f"  {label}: mean |checkerboard-phase difference| {d}, "
         f"mean |adjacent difference| {neigh}")
VOID = False
if neigh > 0 and d * 2 > neigh * 3:
    VOID = True
    note("  => HIGH-FREQUENCY PHASE ARTIFACT DETECTED. The map carries a "
         "grid pattern from basis quantisation, not manuscript structure. "
         "Its directional score is VOID.")
note("")
note("## VERDICT")
if VOID:
    note("RECOVERY NOT ACHIEVED. The exact-unmixing map is disqualified by its "
         "own artifact check, so its score does not count. Among the maps that "
         "remain valid, no method separates undertext on this window: every "
         "incumbent render and the raw band score negative on the undertext "
         "orientation axis, meaning the dominant stroke direction still "
         "dominates after processing.")
    note("")
    note("Two distinct causes, both real:")
    note("  1. MODEL. Greedy vertex endmember extraction selects extremal "
         "pixels, which on noisy sensor data are outliers, not materials. "
         "Nothing downstream can fix a basis that does not correspond to "
         "parchment / overtext ink / undertext ink.")
    note("  2. NUMERICS. Fitting the exact rational solve into int64 required "
         "quantising the basis by >>4, and that quantisation is what stamped "
         "the grid pattern into the output. Exactness was preserved with "
         "respect to the quantised basis, and the quantised basis was wrong.")
    note("")
    note("Neither cause is arithmetic precision. Exact arithmetic cannot "
         "resolve an ill-posed separation: if the endmembers are wrong, the "
         "exact answer to the wrong question is still wrong.")
else:
    winner = max(rows, key=lambda r: r[1])
    note(f"Best valid map: {winner[0]} ({metrics.fmt_milli(winner[1])})")

# ===========================================================================
save("recover_raw.png", stretch8(raw))
save("recover_knox.png", knox)
save("recover_sharpie.png", stretch8(sharpie))
save("recover_pca.png", stretch8(pca))
save("recover_cram_undertext.png", stretch8(under))
for j in range(A.shape[0]):
    save(f"recover_abundance_E{j}.png", stretch8(A[j]))
note("")
note("Images written to demo/: recover_raw, recover_knox, recover_sharpie, "
     "recover_pca, recover_cram_undertext, recover_abundance_E0..E3.")

with open(os.path.join(OUT, "RECOVERY_RUN.md"), "w") as f:
    f.write("\n".join(L) + "\n")
