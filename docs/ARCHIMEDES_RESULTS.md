# Archimedes Palimpsest — Measured Results

Run: `python3 analysis/arc_run.py` · **75,564,310 exact checks, 0 failures**
Data: folio 081r-088v_Arch03r, 15 bands × 3 windows, acquired by receipted
HTTP range requests against the RIT mirror, SHA-256 pinned in
`data/SHA256SUMS.txt`. Full transcript: `demo/ARC_RUN.md`.

Boards addressed: **Board 1** (forgery window — where the incumbent optical
stack recovers nothing) and **Board 2** (control window head-to-head), per
`BENCHMARKS.md` §2.

---

## 1. The 14-bit lattice — confirmed exhaustively

| Check | Result |
|---|---|
| Sample values examined | **70,350,000** (15 bands × 3 windows) |
| Values off the step-4 lattice | **0** |
| Per-band gcd | exactly 4, every band, every window |
| Effective bit depth after sealing | **14** (raw 16-bit container) |
| Seal → unseal round trip | bit-exact, receipted |

The published 16-bit release carries 14-bit sensor data left-shifted by two.
Every tool that has processed this public dataset at face value has been
treating two bits of padding as measurement. The sealing seam
(`cram_dsp/ingest.py`) divides the lattice out once, records the step in the
ledger, and is exactly invertible — so nothing is lost and the cast is
auditable back to the publisher's bytes.

## 2. Band registration audit (NODE-ARC02)

Exact integer search over ±6 px, median-centred per patch so cross-band DC
offset cannot dominate the match. **No resampling is applied** — A1 forbids
correcting evidence into alignment.

- **10 of 15 bands** register at zero shift against LED617.
- Off-reference: LED445 (1,0), LED870 (0,−1), RAKBLL (1,0), RAKIRL (6,0),
  RAKIRR (−6,−2).
- **Margin caveat, stated plainly:** the two raking-IR bands hit the search
  boundary with runner-up margins under 0.02%, meaning their shift estimate
  is *not well determined* by this metric — the raking geometry changes the
  shading field itself, so a translation model is the wrong model for them.
  Declared, not silently "corrected."
- LED617's enormous margin is the trivial self-match against the reference.

## 3. Lane sizing against real deltas (P6, NODE-INF02)

Observed |Δ| on the sealed control band: **0 … 1,930**.

| Lane set | Product | Value-exact to | Verdict on this artifact |
|---|---|---|---|
| (7, 11, 13) | 1,001 | 500 | **aliases — unusable** |
| (11, 13, 17, 19) | 46,189 | 23,094 | covers |
| (7, 11, 13, 17, 19) | 323,323 | 161,661 | covers |

**1,318 real pixels** carry a step exceeding the 8-bit comb's period; each
would be silently misread as Δ mod 1001. The Safe Basis extenders {17, 19}
are load-bearing on genuine 14-bit evidence — the artifact itself selects the
lane set, and it selects one the 8-bit demos never needed.

## 4. Reversibility and reproducibility on real evidence

| Measurement | Result |
|---|---|
| 5/3 wavelet round trip, 524,288 real sensor values | **zero changed** |
| Two independent runs → chain hash | **identical** (`9452753f37e6939c…`) |

Axis C — reproducibility as a certificate rather than a promise — now holds
on a real artifact, not only on synthetic evidence.

## 5. Board 2 — survivability head-to-head (NODE-ARC07)

Same input band, three pipelines. No human labels required: the question is
what each pipeline *destroys*, measured against the artifact's own structure.

| Pipeline | Source lattice preserved | Distinct levels (source 5,085) | Unit-step evidence (source 2,513) |
|---|---|---|---|
| **CRAM reversible round trip** | **100.000%** | **5,085** — every level | **2,513** — exact |
| Incumbent: float blur + round (σ=1) | **25.136%** | 17,226 — inflated by rounding | 1,182 — **53% destroyed** |
| Incumbent: Sharpie band subtraction | **100.000%** | 4,884 | 2,606 — **above source** |

Three findings, reported at the size the evidence supports:

1. **Float blur is destructive on real data, as on synthetic.** Three
   quarters of the lattice structure is gone after one pass, and more than
   half the unit-step evidence with it. The inflated level count is the
   signature: rounding manufactures values the sensor never produced.
2. **Sharpie preserves the lattice exactly — the incumbent wins this axis
   against float blur.** Subtracting two step-4 values leaves a step-4 value;
   the arithmetic is integer-clean. This is recorded because it is true, not
   because it flatters the framework.
3. **Sharpie's cost appears in the last column instead.** Unit-step evidence
   rises *above* the source count — detections that were not in the input.
   That is precisely the noise amplification the incumbent's own authors
   concede in print (`PRIOR_ART.md` §1).

**Null result on the record:** the fingerprint-block statistic reads 2048 of
2048 for every pipeline. On continuous-tone sensor data every block has a
nonzero gcd, so that statistic does not discriminate here. It discriminates
on synthetic requantised evidence (T9) and it does not on this artifact —
stated so the null is not quietly omitted.

## 6. Board 1 — forgery window (NODE-ARC09)

**Incumbent baseline on these folios: nothing recovered; the project
escalated to synchrotron XRF at SLAC.**

Characterization completed under the overpaint:

| Band | Under-paint spread | Substrate spread |
|---|---|---|
| LED365 (UV) | 3,834 | 6,251 |
| LED617 (red) | 1,787 | 10,483 |
| LED870 (IR) | 5,397 | 14,182 |

- Lane-11 and lane-13 class occupancy deviate from uniform by ~0.004% under
  paint and ~0.005–0.006% on substrate — i.e. the residue classes are
  essentially uniformly populated in both regions.
- The unit-step probe fires 2,865 times under paint against 456 on
  substrate — a real asymmetry, but one fully explained by the paint region's
  compressed dynamic range, not by recovered text.

**Verdict: shipped negative on the recovery axis.** The probes run, return
exact reproducible statistics, and produce **no legible-undertext claim**.
Under `BENCHMARKS.md` rule 3 a zero is reported as zero and stays on the
board. No XRF reference is on disk (NODE-ARC08 unresolved), so nothing here
could be corroborated even if it looked promising — and per the corroboration
ladder, an uncorroborated positive on a documented-failure target would not
have been claimable anyway.

The honest summary: the incumbent needed a particle accelerator to read these
folios, and this run does not beat a particle accelerator with reflectance
data. What it does establish is that the substrate, the sealing seam, the
lane sizing, and the receipts all work correctly on the hardest available
real target.

## 7. What this run settles

- Axes **A** (exactness), **B** (reversibility), **C** (reproducibility), and
  **E** (survivability) are now measured on a real artifact, not only on
  synthetic evidence.
- Axis **D** (selectivity) still requires annotated ground truth — NODE-ARC03
  with its HUMAN-VERIFY gate, unexecuted.
- Board 1 closes as a measured negative; Board 2 closes as a measured
  head-to-head with one axis conceded to the incumbent.
