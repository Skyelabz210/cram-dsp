"""CRAM-DF verification harness (T1–T9). Integer-only reporting.

Generates RESULTS.md, receipts.json, and demo PNGs in ./demo/.
Exit code nonzero on any gate failure.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cram_dsp import core, transforms, unmix, forensics, synth
from cram_dsp import baseline_float as foil
from cram_dsp.a1_lint import main as a1_main
from cram_dsp.forensics import Ledger

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo")
os.makedirs(OUT, exist_ok=True)

R = {"checks": 0, "fails": 0}
LINES = []


def pct(n: int, d: int) -> str:
    if d == 0:
        return "n/a"
    q = (100000 * n) // d
    return f"{q // 1000}.{q % 1000:03d}%"


def milli(v: int) -> str:
    return f"{v // 1000}.{v % 1000:03d}"


def check(name: str, cond: bool, n: int = 1):
    R["checks"] += n
    if not cond:
        R["fails"] += 1
        LINES.append(f"  FAIL — {name}")
    return cond


def note(s: str):
    LINES.append(s)


def stretch_u8(a):
    a = np.asarray(a).astype(np.int64)
    lo = int(a.min())
    rng_ = int(a.max()) - lo
    if rng_ == 0:
        rng_ = 1
    return (((a - lo) * 255 + rng_ // 2) // rng_).astype(np.uint8)


def save_gray(name, arr):
    from PIL import Image
    Image.fromarray(np.asarray(arr).astype(np.uint8), mode="L").save(
        os.path.join(OUT, name))


def save_rgb(name, arr):
    from PIL import Image
    Image.fromarray(np.asarray(arr).astype(np.uint8), mode="RGB").save(
        os.path.join(OUT, name))


# ===========================================================================
note("## T1 — Substrate: Dual-Track K-Elimination (star family, composite, tower)")
# exhaustive STAR8
X = np.arange(0, 36 * 37, dtype=np.int64)
k = core.STAR8.k_map(X)
ok = bool(np.array_equal(k, X // 36))
check("STAR8 exhaustive k == floor(X/36) over [0,1332)", ok, 1332)
der = X % 36 + k * 36
check("STAR8 derive() == X (emission seam)", bool(np.array_equal(der, X)), 1332)
kg = ((X % 37 - X % 36) * core.STAR8.Minv) % 37
check("STAR8 subtraction collapse == general formula", bool(np.array_equal(k, kg)), 1332)

# exhaustive STAR16 (Fermat-adjacent 256/257)
X = np.arange(0, 256 * 257, dtype=np.int64)
check("STAR16 exhaustive k == floor(X/256) over [0,65792)",
      bool(np.array_equal(core.STAR16.k_map(X), X // 256)), 65792)

# star family c-rule: A = c*M + 1  ->  M^{-1} mod A = A - c (constructor asserts)
for c in range(1, 201):
    core.DualTrack(36, 36 * c + 1)
check("star family c=1..200: M^{-1} mod A == A-c (vs ext-Euclid)", True, 200)

# Addressing-Layer fault line: fully composite pair (coprimality suffices)
Mc, Ac = 1800, 1001          # 8*9*25  and  7*11*13 — both composite
dtc = core.DualTrack(Mc, Ac)
X = np.arange(0, Mc * Ac, dtype=np.int64)
check(f"composite/composite ({Mc},{Ac}) exhaustive k == floor(X/M)",
      bool(np.array_equal(dtc.k_map(X), X // Mc)), Mc * Ac)

# big adjacent pair with composite anchor 30031 = 59*509
dt6 = core.DualTrack(core.M6, core.M6 + 1)
rng = np.random.default_rng(7)
X = rng.integers(0, dt6.range, size=200_000, dtype=np.int64)
check("(30030,30031) adjacent star, 200k random k == floor(X/M)",
      bool(np.array_equal(dt6.k_map(X), X // core.M6)), 200_000)

# Tower K-Elimination over (36, 37, 73) — exhaustive
tower_ok = True
for x in range(36 * 37 * 73):
    K, xr = core.tower_k((x % 36, x % 37, x % 73), (36, 37, 73))
    if K != x // 36 or xr != x:
        tower_ok = False
        break
check("tower (36,37,73) exhaustive over [0,97236): K and X recovered",
      tower_ok, 36 * 37 * 73)
note(f"  substrate checks: {1332*3 + 65792 + 200 + 1800*1001 + 200000 + 36*37*73:,}")

# ===========================================================================
note("\n## T2 — KELD stratification (exact floor(L/M) via residue pair)")
L = np.arange(256, dtype=np.int64)
check("KELD-8 exhaustive 0..255: K == L//36", bool(np.array_equal(core.keld_map(L), L // 36)), 256)
L = np.arange(65536, dtype=np.int64)
check("KELD-16 exhaustive 0..65535: K == L//256",
      bool(np.array_equal(core.keld_map(L, core.STAR16), L // 256)), 65536)

codex, K_true = synth.make_codex_page()
Kmap, masks = core.keld_masks(codex)
check("codex strata: KELD masks == ground-truth bands (pixel-perfect)",
      bool(np.array_equal(Kmap, K_true)), int(codex.size))
iso = core.keld_isopleth(codex, 3)
note(f"  111=3A isopleth silhouette pixels: {int(iso.sum())} "
     f"(K<3 vs K>=3 boundary; band map is exact, the pigment table is per-corpus calibration)")

PAL = {0: (20, 20, 20), 1: (90, 70, 50), 2: (200, 40, 40), 3: (40, 90, 200),
       4: (210, 190, 150), 5: (235, 225, 200), 6: (255, 255, 255), 7: (255, 0, 255)}
rgb = np.zeros((*Kmap.shape, 3), dtype=np.uint8)
for kk, ccol in PAL.items():
    rgb[Kmap == kk] = ccol
save_rgb("codex_keld_strata.png", rgb)
save_gray("codex_isopleth.png", (iso * 255))

# ===========================================================================
note("\n## T3 — Shadow lane probes (straddle, Sqr-carry, lane-comb selective-Δ)")
# QR/QNR Complement Straddle Lemma — exhaustive
pairs = [(a, (11 - a) % 11) for a in range(1, 11)]
ok = all(((a in core.QR11) != (b in core.QR11)) for a, b in pairs)
check("straddle lemma exhaustive: nonzero complement pairs mod 11 straddle QR/QNR", ok, 10)

# Sqr-carry fire sets, exhaustively derived and verified over 0..255
fire11 = core.sqr_carry_fire_set(11)
v = np.arange(256, dtype=np.int64)
check(f"sqr_carry lane 11 fires exactly on residues {fire11} (0..255 exhaustive)",
      bool(np.array_equal(core.sqr_carry(v, 11) == 1, np.isin(v % 11, fire11))), 256)
fire13 = core.sqr_carry_fire_set(13)
check(f"sqr_carry lane 13 fires exactly on residues {fire13} (0..255 exhaustive)",
      bool(np.array_equal(core.sqr_carry(v, 13) == 1, np.isin(v % 13, fire13))), 256)
try:
    core.sqr_carry(v, 7)
    check("A8 guard: Sqr on lane 7 refused", False)
except ValueError:
    check("A8 guard: Sqr on lane 7 refused", True)

# Faint-ink palimpsest
img, masks3, edges = synth.make_faint_page()
ink_e, d11_e, d12_e = edges["ink"], edges["d11"], edges["d12"]
E = int(ink_e.sum())

comb = core.selective_delta(img, (1, -1), lanes=(7, 11, 13))
tp = int((comb & ink_e).sum())
fpx = int((comb & ~ink_e).sum())
note(f"  lane-comb (7,11,13) selective ±1: precision {pct(tp, tp + fpx)} "
     f"({tp}/{tp + fpx}), recall {pct(tp, E)} ({tp}/{E} ink edges)")
check("lane-comb selective ±1 catches every ink edge", tp == E, E)
check("lane-comb selective ±1 zero false fires", fpx == 0, 1)

# T3b — residue-only regime: the full-width image never exists
lanes_only = {p: (img % p) for p in (7, 11, 13)}
hit = None
for delta in (1, -1):
    h = None
    for p, r_lane in lanes_only.items():
        t = (np.diff(r_lane, axis=1) % p) == (delta % p)
        h = t if h is None else (h & t)
    hit = h if hit is None else (hit | h)
check("residue-only detection (evidence held as lane trays alone): identical map",
      bool(np.array_equal(hit, comb)), 1)
note("  residue-only regime: detection ran on the three lane trays with the "
     "full-width image absent — depth-1 per-lane equality tests, zero cross-lane "
     "data flow (A2/i.i.d. preserved). The classical band-pass |d|==1 has no d to "
     "threshold here: magnitude exists in no lane, and forming it is exactly the "
     "reconstruction step this substrate retires. The scoped equivalence above "
     "holds only when a pristine full-width integer image is available and "
     "nothing ever processes it.")

s11 = core.selective_delta(img, (1, -1), lanes=(11,))
alias = int((s11 & d12_e).sum())
note(f"  single-lane σ-11 selective ±1: {alias}/{int(d12_e.sum())} Δ=12 decoy edges "
     f"falsely fire (12 ≡ 1 mod 11 alias) — cross-lane comb rejects all of them: "
     f"{int((comb & d12_e).sum())}")
check("σ-11 alone aliases Δ=12 as ±1 (CRT disambiguation needed)", alias == int(d12_e.sum()), alias)

any11 = core.any_delta(img, lanes=(11,))
anyc = core.any_delta(img, lanes=(7, 11, 13))
miss = int((any11 & d11_e).sum())
hitc = int((anyc & d11_e).sum())
note(f"  Δ=11 blind spot: σ-11-only detector fires on {miss}/{int(d11_e.sum())} Δ=11 edges; "
     f"lane-comb fires on {hitc}/{int(d11_e.sum())}")
check("σ-11-only is blind to Δ=11", miss == 0, 1)
check("lane-comb catches all Δ=11 edges", hitc == int(d11_e.sum()), 1)

d = np.diff(img, axis=1)
base = d != 0
btp = int((base & ink_e).sum())
note(f"  classical any-difference baseline (|d|>=1): recall {pct(btp, E)}, "
     f"precision {pct(btp, int(base.sum()))} ({btp}/{int(base.sum())} fires — plateau "
     f"steps and decoys all fire). A classical integer band-pass |d|==1 could match "
     f"the comb here; the CRAM contribution is doing it natively in residue lanes "
     f"(never materializing d), CRT alias rejection, and A1 survivability below.")

blur = foil.blur_round_int(img)
comb_b = core.selective_delta(blur, (1, -1), lanes=(7, 11, 13))
tp_b = int((comb_b & ink_e).sum())
fp_b = int((comb_b & ~ink_e).sum())
blur2 = foil.blur_round_int(img, 2.0)
comb_b2 = core.selective_delta(blur2, (1, -1), lanes=(7, 11, 13))
tp_b2 = int((comb_b2 & ink_e).sum())
fp_b2 = int((comb_b2 & ~ink_e).sum())
note(f"  after ONE classical float blur+round (sigma=1): recall {pct(tp_b, E)} "
     f"({tp_b}/{E} — {E - tp_b} ink edges irrecoverably lost) and precision "
     f"{pct(tp_b, tp_b + fp_b)} ({fp_b} blur-artifact ±1 fires contaminate the class); "
     f"at sigma=2: recall {pct(tp_b2, E)}, {fp_b2} false fires. The float path is "
     f"irreversible; the CRAM path below loses zero.")
check("float pipeline loses Δ=1 evidence and contaminates the class",
      tp_b < E and (fp_b > fpx or fp_b2 > fpx), 1)

co, sh = transforms.wav2d_fwd(img, 2)
rec = np.array(transforms.wav2d_inv(co, sh), dtype=np.int64)
check("CRAM reversible wavelet round trip: palimpsest bit-exact", bool(np.array_equal(rec, img)), int(img.size))
comb_r = core.selective_delta(rec, (1, -1), lanes=(7, 11, 13))
check("selective-Δ map identical after CRAM round trip", bool(np.array_equal(comb_r, comb)), 1)

save_gray("palimpsest_input_stretched.png", stretch_u8(img))
save_gray("palimpsest_lane_comb_ink.png",
          (np.pad(comb, ((0, 0), (0, 1))) * 255))
save_gray("palimpsest_after_float_blur.png",
          (np.pad(comb_b, ((0, 0), (0, 1))) * 255))

# ===========================================================================
note("\n## T4 — Integer NTT convolution (exact, check-laned, deterministic)")
rng = np.random.default_rng(11)
ntt_ok = True
cl_ok = True
for t in range(30):
    a = rng.integers(-50, 51, size=(12, 12)).astype(np.int64)
    kk = rng.integers(-9, 10, size=(3, 3)).astype(np.int64)
    full = transforms.conv2d_exact(a, kk, mode="full")
    oracle = transforms.conv2d_direct(a, kk)
    if not np.array_equal(full, oracle):
        ntt_ok = False
    if not transforms.check_lane_verify(a, kk, full, 17):
        cl_ok = False
check("30 random NTT convolutions == unbounded-int oracle (bit-exact)", ntt_ok, 30 * 14 * 14)
check("INV-8-style mod-17 check lane agrees on all 30", cl_ok, 30)

ker, den = transforms.binomial_kernel(2)
crop = codex[:64, :64]
num = transforms.conv2d_exact(crop, ker, mode="same")
check("binomial demo check lane (p=17)",
      transforms.check_lane_verify(crop, ker, transforms.conv2d_exact(crop, ker, mode="full"), 17), 1)
disp = transforms.emit_round_div(num, den)
save_gray("codex_binomial_blur_emitted.png", stretch_u8(disp))
h1 = Ledger.digest(num)
h2 = Ledger.digest(transforms.conv2d_exact(crop, ker, mode="same"))
check("NTT determinism: identical digest across two runs", h1 == h2, 1)
note(f"  kernel carried as exact (numerator, denominator={den}); the single "
     f"rounding division happens only at the emission seam")

# ===========================================================================
note("\n## T5 — Reversible transforms (Transduction layer) + Kill #113")
rng = np.random.default_rng(13)
ok = True
n1d = 0
for t in range(400):
    n = int(rng.integers(1, 41))
    x = [int(v) for v in rng.integers(-999, 1000, size=n)]
    s, dd = transforms.fwd53(x)
    if transforms.inv53(s, dd) != x:
        ok = False
    n1d += n
check("LeGall 5/3 1D: 400 random round trips bit-exact", ok, n1d)

shapes_to_try = [(1, 7), (5, 1), (17, 23), (33, 40), (64, 64), (96, 128)]
ok = True
npx = 0
for (hh, ww) in shapes_to_try:
    for lev in (1, 2, 3):
        a = rng.integers(0, 65536, size=(hh, ww)).astype(np.int64)
        co, sh = transforms.wav2d_fwd(a, lev)
        rec = np.array(transforms.wav2d_inv(co, sh), dtype=np.int64)
        if not np.array_equal(rec, a):
            ok = False
        npx += hh * ww
check("5/3 2D multilevel: all shapes/levels bit-exact (incl. odd, 16-bit)", ok, npx)

Rc = rng.integers(0, 65536, size=200_000).astype(np.int64)
Gc = rng.integers(0, 65536, size=200_000).astype(np.int64)
Bc = rng.integers(0, 65536, size=200_000).astype(np.int64)
Y, U, V = transforms.rct_fwd(Rc, Gc, Bc)
r2, g2, b2 = transforms.rct_inv(Y, U, V)
check("RCT 200k random 16-bit triples: bit-exact inverse",
      bool(np.array_equal(r2, Rc) and np.array_equal(g2, Gc) and np.array_equal(b2, Bc)), 200_000)

bands = [rng.integers(0, 256, size=(24, 32)).astype(np.int64) for _ in range(5)]
di = transforms.chromadi_fwd(bands)
bk = transforms.chromadi_inv(di)
check("reversible ChromaDI (5 bands): bit-exact inverse",
      all(np.array_equal(x, y) for x, y in zip(bands, bk)), 5 * 24 * 32)

ok = True
for t in range(50):
    a = rng.integers(-500, 500, size=(20, 30)).astype(np.int64)
    if transforms.skew_energy_ip(a, 1) != 0 or transforms.skew_energy_ip(a, 0) != 0:
        ok = False
check("Kill #113: <I, D_skew I> == 0 exactly, 50 random images, both axes", ok, 100)

# ===========================================================================
note("\n## T6 — Rational-Grid Exact Unmixing vs float PCA")
Sr, Sv, Yr, Yv, (p, q) = synth.make_bleed_pair()
Sr_h, Sv_h, viol = unmix.unmix_exact(Yr, Yv, p, q)
check("exact unmix at true (3,8): zero divisibility violations", viol == 0, int(Yr.size) * 2)
check("recto recovered exactly (zero error)", bool(np.array_equal(Sr_h, Sr)), int(Sr.size))
check("verso recovered exactly (zero error)", bool(np.array_equal(Sv_h, Sv)), int(Sv.size))
(pe, qe), score = unmix.estimate_pq(Yr, Yv)
check(f"blind rational-grid estimator finds (p,q)=({pe},{qe})", (pe, qe) == (3, 8), 1)
note(f"  estimator score (violations, negatives, cross-energy): {score}")
m1, m2 = foil.pca_best_mae_milli(Yr, Yv, Sr, Sv)
note(f"  float PCA baseline best-fit MAE: recto {milli(m1)}, verso {milli(m2)} "
     f"(intensity units) vs CRAM exact 0.000 — given a rational mixing operator; "
     f"blind estimation is over the coprime grid q<=12")
tri = np.hstack([stretch_u8(Yr), np.full((96, 4), 255, np.uint8),
                 stretch_u8(Sr_h), np.full((96, 4), 255, np.uint8),
                 stretch_u8(Sr)])
save_gray("unmix_mixed_recovered_truth.png", tri)

# ===========================================================================
note("\n## T7 — Provenance: hash-chained receipts (computational chain of custody)")

def pipeline(im):
    Lg = Ledger()
    d0 = Lg.digest(im)
    co, sh = transforms.wav2d_fwd(im, 2)
    ca = np.array(co, dtype=np.int64)
    Lg.record("wav53_fwd", {"levels": 2}, d0, Lg.digest(ca))
    rec = np.array(transforms.wav2d_inv(co, sh), dtype=np.int64)
    Lg.record("wav53_inv", {"levels": 2}, Lg.digest(ca), Lg.digest(rec))
    okr = Lg.roundtrip_receipt("wav53", im, rec)
    return Lg, okr

L1, ok1 = pipeline(img)
L2, ok2 = pipeline(img)
check("round-trip receipt: original bytes recovered exactly", ok1 and ok2, 1)
check("two independent runs -> identical chain hash (bit-identical pipeline)",
      L1.chain == L2.chain, 1)
with open(os.path.join(OUT, "receipts.json"), "w") as f:
    f.write(L1.export())
note(f"  chain head: {L1.chain[:32]}…  ({len(L1.entries)} receipts, receipts.json exported)")

# ===========================================================================
note("\n## T8 — Exact copy-move clone detection")
cm_img, cm_truth = synth.make_copy_move()
mask, prs = forensics.copy_move_exact(cm_img, block=12, stride=2, min_offset=16)
inter, union = forensics.iou(mask, cm_truth)
check(f"copy-move IoU exact: {inter}/{union}", inter == union and union == int(cm_truth.sum()),
      int(cm_truth.sum()))
note(f"  {len(prs)} matching block pairs; detected mask == planted clone exactly")
save_gray("copymove_mask.png", (mask * 255))

# ===========================================================================
note("\n## T9 — Quantization-fingerprint splice localization + float erasure")
sp_img, sp_mask = synth.make_splice()
fp = forensics.quant_fingerprint_map(sp_img, block=16)
flags, step = forensics.splice_flag_map(fp)
truth_blocks = sp_mask.reshape(6, 16, 8, 16).any(axis=(1, 3))
bi, bu = forensics.iou(flags, truth_blocks)
note(f"  estimated background step: {step}; block IoU {bi}/{bu} "
     f"(interior fp=5, seam blocks collapse to gcd 1 — both flagged)")
check("splice localization: flagged blocks == blocks touching the paste",
      bi == bu, int(truth_blocks.sum()))

before = int(((fp != 0) & (fp % 4 == 0)).sum())
fp_b = forensics.quant_fingerprint_map(foil.blur_round_int(sp_img), block=16)
after = int(((fp_b != 0) & (fp_b % 4 == 0)).sum())
note(f"  background-fingerprint blocks before float blur: {before}; after: {after} — "
     f"one classical float op erases the requantization history irreversibly")
check("float blur destroys the fingerprint", after * 4 <= before, 1)
co, sh = transforms.wav2d_fwd(sp_img, 2)
rec = np.array(transforms.wav2d_inv(co, sh), dtype=np.int64)
check("A1 pipeline preserves it: wavelet round trip bit-exact, fingerprint intact",
      bool(np.array_equal(rec, sp_img)) and
      bool(np.array_equal(forensics.quant_fingerprint_map(rec, 16), fp)), 1)
panel = np.hstack([stretch_u8(sp_img), np.full((96, 4), 255, np.uint8),
                   stretch_u8(np.kron(flags.astype(np.int64), np.ones((16, 16), np.int64)) * 255)])
save_gray("splice_fingerprint_flags.png", panel)

# ===========================================================================
note("\n## T10 — Lane sizing vs. source bit depth (Safe Basis selection theorem)")
# A lane set L is value-exact for steps |d| <= floor((prod(L)-1)/2): the joint
# residue class fixes d mod prod(L), and two candidates within that bound cannot
# be congruent unless equal. Verify the bound is TIGHT by exhibiting the first
# aliasing pair for each lane set, and confirm S8 lanes cover 14-bit evidence.
LANESETS = [(7, 11, 13), (11, 13, 17, 19), (7, 11, 13, 17, 19)]
for L in LANESETS:
    Pr = 1
    for p in L:
        Pr *= p
    bound = (Pr - 1) // 2
    # exhaustive within bound: no two distinct deltas share a joint residue class
    lo, hi = -min(bound, 400), min(bound, 400)
    seen = {}
    collide = False
    for d in range(lo, hi + 1):
        key = tuple(d % p for p in L)
        if key in seen:
            collide = True
        seen[key] = d
    check(f"lanes {L}: no aliasing within +/-{min(bound,400)}", not collide, hi - lo + 1)
    # tightness: d and d+Pr are always confounded
    check(f"lanes {L}: bound tight (d and d+{Pr} alias)",
          all((d % p) == ((d + Pr) % p) for p in L for d in (1, 7, 100)), 1)
    note(f"  {L}: product {Pr:,} -> value-exact for |d| <= {bound:,}"
         f"  {'covers' if bound >= 16383 else 'DOES NOT cover'} 14-bit evidence (|d| <= 16,383)")
note("  => the 8-bit demos above run on (7,11,13); the 14-bit Archimedes rasters "
     "require the Safe Basis extenders {17,19} — S8 is load-bearing for real "
     "forensic bit depths, not decorative.")

# ===========================================================================
note("\n## A1 lint (static compliance)")
verdict, lint_lines = a1_main(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cram_dsp"))
note(f"  {verdict}")
LINES.extend(lint_lines)
check("A1 lint passes on all production files", verdict.startswith("A1 LINT: PASS"), 1)

# ===========================================================================
hdr = [
    "# CRAM-DF — Verification Results",
    "",
    f"**{R['checks']:,} exact checks — {R['fails']} failures.**",
    "All arithmetic integer-exact (A1); no Garner/mixed-radix anywhere (A2); all lane",
    "operators standard CRT homomorphisms, so the A3 distortion certificate is trivial",
    "(Gamma = 1); the sanctioned Sqr probe runs on lanes 11/13 only, never lane 7.",
    "",
]
with open(os.path.join(OUT, "RESULTS.md"), "w") as f:
    f.write("\n".join(hdr + LINES) + "\n")

print("\n".join(hdr + LINES))
print(f"\nTOTAL: {R['checks']:,} checks, {R['fails']} failures")
sys.exit(1 if R["fails"] else 0)
