# CRAM-DF — Residue-Native Forensic Digital Processing

A complete, tested engine for forensic digital processing built on the CRAM
substrate: exact multi-band separation, latent-structure probes, tamper
localization, and a computational chain of custody. Sources: the CRAM-DIP
packet (KELD, Shadow-11, integer NTT), the manuscript-imaging research report
(Tonazzini et al. 2019 landscape + Archimedes/Herculaneum data), and the two
attached ideation docs — CRAM-UNIFIED (Kill #113, Sqr-carry stratification,
INV-8 check lane) and the CRAM Formalization (addressing/field fault line,
adjacency collapse, tower generalization).

## Ideate

The classical forensic DIP pipeline read through the CRAM lens (full index in
CRAM_OPPORTUNITY_REPORT.md): float PCA/ICA separation is an A1 violation that
leaves residual by construction; float FFT enhancement rings and drifts;
magnitude/banding is done by positional decode (reconstruction-shaped);
bit-plane forensics is locked in-band to base 2; and — the decisive one —
every float op on evidence irreversibly erases exact structure the analyst
needed. Each entry routes to a construct built below. The forensic domain is
unusually well matched to the substrate: courts need bit-identical
reproducibility and invertible processing, which is precisely what A1 + A2
deliver and floating point cannot.

## Innovate

Constructs built and verified this session (★ = sourced from the attached
ideation docs):

1. **Lane-Comb Selective-Δ Probe** — exact-value-selective step detection
   computed entirely in residue lanes (7, 11, 13); the integer difference is
   never materialized. The joint class identifies the step mod 1001, so the
   probe is value-selective for |d| ≤ 500. Witnessed: 100% precision/recall on
   Δ=+1 undertext; the 12 ≡ 1 (mod 11) alias that fools a single lane is
   rejected by the comb; the Δ=11 single-lane blind spot is closed.
2. **KELD + KELD-16** — K-Elimination Luminance Decode as exact residue-native
   banding: K = floor(L/36) read from (r36, r37) by one subtraction; extended
   to 16-bit on the Fermat-adjacent pair (256, 257). The band map is exact;
   the pigment table rides on top as per-corpus calibration.
3. ★ **Tower K-Elimination** (`core.tower_k`) — multi-level winding recovery
   across pairwise-coprime anchors, O(levels), all residue-space; exhaustive
   over (36, 37, 73).
4. **Rational-Grid Exact Unmixing** — recto-verso bleed-through inverted
   fraction-free (D = q²−p²), zero error at the true rational operator; blind
   estimation over the coprime grid by an integer objective (divisibility
   violations → negativity → cross-energy). Float PCA foil leaves milli-MAE
   thousands of units above zero on the same input.
5. **Reversible ChromaDI** — the review article's false-colour band
   differences made losslessly invertible (base band retained).
6. **Computational chain of custody** — the kiosk verification-receipt idea as
   a SHA-256 hash-chained operation ledger. Because the pipeline is A1, two
   independent runs produce the identical chain head: the hash IS the
   reproducibility certificate, and round-trip receipts witness T-X-REV on the
   actual evidence bytes.
7. **Requantization fingerprint + Float-Erasure result** — per-block gcd of
   local steps localizes spliced regions with different processing histories
   (seam blocks collapse to gcd 1 and self-flag). One classical float blur
   destroys the fingerprint (28 → 0 blocks) and the Δ=1 class (26/114 edges
   lost, 682 contaminating fires); the A1 path loses zero, ever.
8. ★ **INV-8 software check lane** — independent mod-17 recomputation verifies
   the NTT engine's algebraic integrity in parallel on every tested run.
9. ★ **Kill #113 witness** — the exact skew-symmetric operator with
   ⟨I, D I⟩ = 0 identically over ℤ: iterative filtering cannot leak energy
   into synthetic noise.
10. ★ **Generalized Sqr-carry stratification** on shadow-channel lanes 11 and
    13, fire sets derived (not assumed), with the A8 guard: Sqr on lane 7 is
    refused programmatically.
11. **A1 linter** — AST-level compliance tooling (float literals, true
    division, float names) with quarantine + self-exempt discipline.

## Design

Package `cram_df/`: `core` (Safe Basis, DualTrack star family, KELD, shadow
probes, lane comb, tower), `transforms` (NTT convolution over P = 998244353
with exact rational kernels, RCT, ChromaDI, LeGall 5/3 lifting, Kill #113,
check lane), `unmix`, `forensics` (Ledger, copy-move, fingerprint/splice),
`synth` (seeded integer evidence), `baseline_float` (quarantined foils),
`a1_lint`. Harness: `run_all.py`.

Compliance: **A1** — lint PASS on all production files; the single sanctioned
rounding division lives at the emission seam (`emit_round_div`); PNG export is
the sealed boundary. **A2** — no Garner, no mixed-radix, no positional decode
anywhere; KELD/tower stay in residue space; `derive()` exists only for
display/audit seams. **A3** — every lane operator used is a standard CRT ring
homomorphism, so the distortion certificate is trivial (Γ = 1); the Sqr probe
is read-only on lanes 11/13. **Fault line** — the addressing layer runs on
coprimality alone, witnessed on fully composite dual tracks (1800, 1001) and
(30030, 30031); no field-layer op is needed anywhere in the pipeline.
**DKAM** — the only degree-2 operator is the sanctioned shadow probe; ρ = 3 >
d = 2. Inverses via extended Euclid (`pow(a, -1, m)`) only — never Fermat.

## Test

RESULTS.md carries the full run: **2,582,984 exact checks, 0 failures** —
substrate exhaustives (star8/star16/composite/tower ≈ 2.17M), KELD exhaustive
8/16-bit + pixel-perfect codex strata, shadow-probe theorems verified
exhaustively, 30 NTT-vs-oracle equalities + check lane + determinism digest,
all reversible round trips bit-exact (1D/2D/multilevel/RCT/ChromaDI), Kill
#113 zero on 100 cases, exact unmixing + blind estimation, identical
provenance chains across runs, copy-move IoU exact, splice block IoU 20/20,
and both float-erasure demonstrations. Calibrations are folded inline in
RESULTS.md at the size the evidence supports — in particular: the selective-Δ
comb is class-selective (not magnitude-selective), a classical integer
band-pass could match it on clean integers, and the differentiators are
residue-native operation, CRT alias rejection, and A1 survivability.

## Build

`python3 run_all.py` reproduces everything (deterministic, seeded). Library
use: `from cram_df import core, transforms, unmix, forensics`. Deliverables:
`cram_df.zip`, RESULTS.md, receipts.json, demo images, this document, the DAG
record, and the opportunity index.

Phase 2 queue: Rust/NEON port of the lane ops and NTT per the MANA pattern;
real-data run on the Archimedes Palimpsest open TIFFs
(archimedespalimpsest.net / RIT mirror) — KELD strata, ChromaDI, lane-comb
probes, and unmixing on actual folios; full Hao–Shi integer RKLT as the next
reversible decorrelator, completing Design 1 of the research report (Designs 1
and 4 are realized here in fixed-decorrelator + exact-unmixing form).
Positioning: CRAM-DF is the processing layer downstream of any acquisition
modality — MSI, XRF, THz, RTI, or a phone camera — wherever the evidence is
integers and the court needs the pipeline to be exact, reversible, and
reproducible.
