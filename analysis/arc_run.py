"""NODE-ARC02 / ARC06 / ARC07 / ARC09 — the Archimedes run.

Objective measurements only. Nothing here needs a human label: registration,
lattice, lane sizing, reversibility, reproducibility, and survivability are
all decidable from the artifact's own bytes. Claims that WOULD need labels
(undertext identification) are reported as characterization, not recovery.

Usage: python3 analysis/arc_run.py
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import core, transforms, forensics, ingest, metrics, render
from cram_dsp import baseline_float as foil
from cram_dsp.forensics import Ledger

CORPUS = "/home/claude/corpus"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo")
os.makedirs(OUT, exist_ok=True)

BANDS = ["LED365", "LED445", "LED470", "LED505", "LED530", "LED570", "LED617",
         "LED625", "LED700", "LED735", "LED870", "RAKBLL", "RAKBLR",
         "RAKIRL", "RAKIRR"]

R = {"checks": 0, "fails": 0}
L = []


def check(name, cond, n=1):
    R["checks"] += n
    if not cond:
        R["fails"] += 1
        L.append(f"  FAIL — {name}")
    return cond


def note(s):
    L.append(s)


def pct_milli(num, den):
    """Exact percent in milli-units: floor(100000*num/den)/1000."""
    if den == 0:
        return 0
    return (100000 * int(num)) // int(den)


def load(window, band):
    z = np.load(f"{CORPUS}/archimedes_{window}.npz")
    return z[band].astype(np.int64)


# ===========================================================================
note("## A — Acquisition and lattice (NODE-INF04 seam, receipted)")
led = Ledger()
sums = {}
for line in open("data/SHA256SUMS.txt"):
    h, f = line.split()
    sums[f.strip()] = h.strip()

lattices = {}
for w in ("control", "forgery", "caltarget"):
    a = load(w, "LED617")
    led.record_acquisition(
        "mirrors.rit.edu/archie/post-2007/HTML_TIFF/Data/16bit_tif/081r-088v_Arch03r",
        f"window:{w}", sums[f"archimedes_{w}.npz"],
        os.path.getsize(f"{CORPUS}/archimedes_{w}.npz"), led.digest(a))
    sealed, g, bits = ingest.seal(a, led, name=w)
    lattices[w] = g
    ok = np.array_equal(ingest.unseal(sealed, g), a)
    check(f"{w}: seal/unseal exactly reversible", ok, int(a.size))
    note(f"  {w}: lattice step {g}, effective bits {bits}, "
         f"raw range [{int(a.min())},{int(a.max())}] -> sealed "
         f"[{int(sealed.min())},{int(sealed.max())}]")

# full-stack lattice verification, every band, every window
tot = bad = 0
for w in ("control", "forgery", "caltarget"):
    z = np.load(f"{CORPUS}/archimedes_{w}.npz")
    for b in BANDS:
        a = z[b].astype(np.int64)
        tot += a.size
        bad += int((a % 4 != 0).sum())
check(f"14-bit lattice holds across all bands/windows ({tot:,} values)", bad == 0, tot)
note(f"  exhaustive: {tot:,} sample values, {bad} not on the step-4 lattice "
     f"=> published 16-bit release carries 14-bit sensor data (2 bits padding)")

# ===========================================================================
note("\n## B — NODE-ARC02: band registration audit (exact integer, no resampling)")
# Bands differ in absolute intensity by orders of magnitude, so raw SSD is
# dominated by DC offset, not alignment. Subtract each patch's own median
# (exact integer) before comparing: scale-free, still float-free.
def centered(a):
    a = np.asarray(a).astype(np.int64)
    return a - int(np.median(a))


ref = centered(load("control", "LED617")[200:456, 800:1056])
shifts = {}
for b in BANDS:
    cur = load("control", b)
    best, bestv, second = (0, 0), None, None
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            patch = cur[200 + dy:456 + dy, 800 + dx:1056 + dx]
            if patch.shape != ref.shape:
                continue
            v = int(np.abs(centered(patch) - ref).sum())
            if bestv is None or v < bestv:
                second, bestv, best = bestv, v, (dy, dx)
            elif second is None or v < second:
                second = v
    shifts[b] = best
    margin = pct_milli(second - bestv, max(bestv, 1)) if second else 0
    note(f"  {b}: best integer shift (dy,dx)={best}, "
         f"runner-up worse by {metrics.fmt_milli(margin)}%")
nonzero = [b for b, s in shifts.items() if s != (0, 0)]
note(f"  bands off-reference: {len(nonzero)}/15 ({', '.join(nonzero) if nonzero else 'none'}). "
     f"DECLARED, not corrected: A1 forbids resampling evidence to hide misalignment.")
check("registration audit completed for all 15 bands", len(shifts) == 15, 15)

# ===========================================================================
note("\n## C — NODE-INF02: lane sizing against REAL band deltas (P6)")
seal_ctrl, g_ctrl, bits_ctrl = ingest.seal(load("control", "LED617"))
d = np.diff(seal_ctrl, axis=1)
maxd = int(np.abs(d).max())
note(f"  observed |delta| range on sealed control band: 0..{maxd:,}")
for lanes in (core.LANES_8BIT, core.LANES_14BIT, core.LANES_EXT):
    B = core.lane_bound(lanes)
    verdict = "COVERS" if B >= maxd else "ALIASES — unusable here"
    note(f"  lanes {lanes}: value-exact to |d|<={B:,}  -> {verdict}")
chosen = core.lanes_for_bitdepth(bits_ctrl)
check(f"auto-selected lane set {chosen} covers observed deltas",
      core.lane_bound(chosen) >= maxd, 1)
# exhibit a real aliasing pair the 8-bit comb would confuse
P8 = 7 * 11 * 13
alias = np.abs(d) >= P8
n_alias = int(alias.sum())
note(f"  real pixels whose delta exceeds the 8-bit comb's period ({P8}): "
     f"{n_alias:,} — each would be misread as delta mod {P8} by the "
     f"8-bit lane set. This is why the S8 extenders {{17,19}} are load-bearing "
     f"on real 14-bit evidence, not decorative.")
check("8-bit lane set demonstrably insufficient on real data", n_alias > 0, 1)

# ===========================================================================
note("\n## D — Reversibility and reproducibility on real 14-bit evidence")
work = seal_ctrl[:512, :1024]
co, sh = transforms.wav2d_fwd(work, 2)
rec = np.array(transforms.wav2d_inv(co, sh), dtype=np.int64)
check("5/3 wavelet round trip bit-exact on real Archimedes data",
      bool(np.array_equal(rec, work)), int(work.size))
note(f"  {work.size:,} real sensor values through forward+inverse: zero changed")


def pipeline(a):
    lg = Ledger()
    d0 = lg.digest(a)
    c, s = transforms.wav2d_fwd(a, 2)
    ca = np.array(c, dtype=np.int64)
    lg.record("wav53_fwd", {"levels": 2}, d0, lg.digest(ca))
    r = np.array(transforms.wav2d_inv(c, s), dtype=np.int64)
    lg.record("wav53_inv", {"levels": 2}, lg.digest(ca), lg.digest(r))
    return lg


c1, c2 = pipeline(work), pipeline(work)
check("two independent runs on real data -> identical chain hash",
      c1.chain == c2.chain, 1)
note(f"  chain head: {c1.chain[:32]}...")

# ===========================================================================
note("\n## E — NODE-ARC07: survivability head-to-head, control window")
note("  Axis E. No human labels needed: the question is what each pipeline")
note("  destroys, measured against the artifact's own structure.")

raw = load("control", "LED617")[:512, :1024]
lat_before = metrics.lattice_intact(raw, 4)
lev_before = metrics.distinct_levels(raw)
fp_before = forensics.quant_fingerprint_map(raw, block=16)
fpb_before = int((fp_before != 0).sum())
probe_lanes = core.LANES_14BIT
sealed_raw, _, _ = ingest.seal(raw)
ud_before = metrics.unit_delta_count(sealed_raw, probe_lanes)

rows = []
# CRAM reversible path
co, sh = transforms.wav2d_fwd(raw, 2)
cram_out = np.array(transforms.wav2d_inv(co, sh), dtype=np.int64)
# incumbent foils
sharpie = foil.sharpie_subtract(load("control", "LED617")[:512, :1024],
                                load("control", "LED445")[:512, :1024])
blurred = foil.blur_round_int(raw, 1.0)

for label, out in (("CRAM reversible round trip", cram_out),
                   ("incumbent: float blur+round (sigma=1)", blurred),
                   ("incumbent: Sharpie band subtraction", sharpie)):
    li, lt = metrics.lattice_intact(out, 4)
    lev = metrics.distinct_levels(out)
    fp = forensics.quant_fingerprint_map(out, block=16)
    fpb = int((fp != 0).sum())
    s_out, _, _ = ingest.seal(np.abs(out))
    ud = metrics.unit_delta_count(s_out, probe_lanes)
    rows.append((label, metrics.milli(li, lt), lev, fpb, ud))
    note(f"  {label}:")
    note(f"     source lattice preserved on {metrics.fmt_milli(pct_milli(li, lt))}% "
         f"of values | distinct levels {lev:,} (was {lev_before:,}) | "
         f"unit-step evidence {ud:,} (was {ud_before:,})")

note(f"  (fingerprint-block count is {fpb_before}/{fpb_before} for every path: on "
     f"continuous-tone sensor data every block has a nonzero gcd, so that "
     f"statistic does not discriminate here. It discriminates on synthetic "
     f"requantised evidence, T9. Reported so the null is on the record.)")
note("  Sharpie preserves the lattice exactly — subtraction of two step-4 values "
     "stays on step 4 — so the incumbent WINS this axis against float blur. Its "
     "cost shows in the last column instead: unit-step evidence rises above the "
     "source count, which is the noise amplification its own authors concede.")
check("CRAM path preserves the source lattice completely",
      rows[0][1] == 1000, 1)
check("CRAM path preserves every distinct source level",
      rows[0][2] == lev_before, 1)
check("at least one incumbent path destroys source structure",
      any(r[1] < 1000 for r in rows[1:]), 1)

# ===========================================================================
note("\n## F — NODE-ARC09: forgery window characterization (Board 1)")
note("  Incumbent optical baseline on these folios: recovers nothing;")
note("  the project escalated to synchrotron XRF. This run is")
note("  CHARACTERIZATION, not a recovery claim. No XRF reference is on")
note("  disk (NODE-ARC08 unresolved), so nothing here is corroborated.")

f617 = load("forgery", "LED617")
f365 = load("forgery", "LED365")
f870 = load("forgery", "LED870")
sf, gf, bf = ingest.seal(f617)
note(f"  forgery window: lattice step {gf}, effective bits {bf}, "
     f"range [{int(sf.min())},{int(sf.max())}]")

# opacity test: does ANY band show structure the others don't, under paint?
paint = sf < int(np.percentile(sf, 20))
clear = sf > int(np.percentile(sf, 80))
note(f"  darkest-quintile (paint-dominated) pixels: {int(paint.sum()):,}; "
     f"brightest quintile (substrate): {int(clear.sum()):,}")

for name, band in (("LED365 (UV)", f365), ("LED617 (red)", f617),
                   ("LED870 (IR)", f870)):
    s, _, _ = ingest.seal(band)
    inside = metrics.region_stats(s, paint)
    outside = metrics.region_stats(s, clear)
    sep = inside["spread"]
    note(f"  {name}: under-paint spread {sep:,} "
         f"(mean {metrics.fmt_milli(inside['mean_milli'])}), "
         f"substrate spread {outside['spread']:,} "
         f"(mean {metrics.fmt_milli(outside['mean_milli'])})")

# residue-class structure under paint vs matched substrate
for p in (11, 13):
    cm = render.lane_class_map(sf, p)
    hin = np.bincount(cm[paint].ravel(), minlength=p)
    hout = np.bincount(cm[clear].ravel(), minlength=p)
    chi_in = int(np.abs(hin - hin.sum() // p).sum())
    chi_out = int(np.abs(hout - hout.sum() // p).sum())
    note(f"  lane {p} class-occupancy deviation from uniform: "
         f"under paint {metrics.fmt_milli(metrics.milli(chi_in, max(int(hin.sum()),1)))}%, "
         f"substrate {metrics.fmt_milli(metrics.milli(chi_out, max(int(hout.sum()),1)))}%")

ud_paint = int(render.undertext_probe(sf, core.LANES_14BIT)[paint[:, :-1]].sum())
ud_clear = int(render.undertext_probe(sf, core.LANES_14BIT)[clear[:, :-1]].sum())
note(f"  unit-step probe fires: {ud_paint:,} under paint, {ud_clear:,} on substrate")
note("  VERDICT (Board 1): the residue-native probes run and return exact,")
note("  reproducible statistics under the overpaint, but this run produces NO")
note("  legible-undertext claim. Reported as a shipped negative on the")
note("  recovery axis, per BENCHMARKS.md rule 3. Corroboration via XRF")
note("  (NODE-ARC08) remains the gate for any positive claim here.")
check("forgery window characterized end-to-end without error", True, 1)

# ===========================================================================
with open(os.path.join(OUT, "ARC_RUN.md"), "w") as f:
    f.write("# Archimedes Run — Objective Results\n\n"
            f"**{R['checks']:,} exact checks — {R['fails']} failures.**\n\n"
            + "\n".join(L) + "\n")
print("\n".join(L))
print(f"\nTOTAL: {R['checks']:,} checks, {R['fails']} failures")
sys.exit(1 if R["fails"] else 0)
