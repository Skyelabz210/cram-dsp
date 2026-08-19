# CRAM-DSP

**Residue-native digital signal and image processing for forensic work.**
Exact integer arithmetic end to end, reversible transforms, and a hash-chained
chain of custody for computation.

Anthony Diaz (Acid) — HackFate Research / Skyelabz210.
Framework: Configurable Residue Arithmetic Machine (CRAM) / Quantum-Modular
Number Framework (QMNF).

```
2,585,391 exact checks   ·   0 failures   ·   A1 lint PASS
```

---

## What this is

Forensic image analysis asks what an artifact *contains*. Floating-point
pipelines answer a different question — what an artifact *approximately* looks
like after processing — and they answer it irreversibly. Measured here: one
standard float blur destroys 26 of 114 unit-amplitude ink edges, injects 682
false detections into that class, and erases every requantization fingerprint on
the page. Nothing recovers them.

CRAM-DSP runs the whole pipeline in exact integers on the CRT torus. Magnitude is
recovered by K-Elimination — one modular subtraction — instead of by
reconstruction, so residue lanes stay independent. Every transform is a bijection
on integers. Every operation appends a SHA-256 receipt, and because the pipeline
is deterministic, two independent runs commit to the same chain hash: the hash
*is* the reproducibility certificate.

## Claims at a glance

| Claim | Evidence |
|---|---|
| Exact layer separation where the mixing operator is rational | 0 error vs float PCA's MAE 2.296 / 4.899 on identical input |
| Exact stratification without decoding magnitude | `floor(L/M)` from a residue pair, exhaustive at 8- and 16-bit |
| Detection with the full-width image absent | identical 114/114 map computed from lane trays alone |
| CRT alias rejection | Δ=12 confounder that fools a single lane rejected by the comb; Δ=11 blind spot closed |
| Evidence survives processing | 114/114 edges and 28/28 fingerprint blocks after round trip; float path loses all |
| Reproducibility | identical chain hash across independent runs |
| Real-artifact finding, first contact | the Archimedes release is 14-bit data in a 16-bit container — 70,350,000 values, 0 exceptions |

Every one is scoped in `METRICS.md` and proved in `PROOFS.md`. Where a result
overlaps existing methods, the axis, conditions, and location of the
differentiation are stated — see `COMPARISONS.md`.

## Quick start

```bash
python3 run_all.py          # full T1–T10 suite + A1 lint -> demo/RESULTS.md
```

```python
from cram_dsp import core, transforms, unmix, forensics

K      = core.keld_map(img)                                    # exact band index
ink    = core.selective_delta(img, (1, -1), lanes=(7, 11, 13)) # residue-native probe
co, sh = transforms.wav2d_fwd(img, levels=2)                   # reversible
rec    = transforms.wav2d_inv(co, sh)                          # bit-exact
led    = forensics.Ledger(); led.roundtrip_receipt("wav53", img, rec)
```

Requires Python 3, numpy, Pillow. Deterministic and seeded.

## Read in this order

1. **`MANIFEST.md`** — full inventory, every file and its gate
2. **`PROOFS.md`** — P1–P13, each with proof and its witnessing test
3. **`METRICS.md`** — measurement contract, six scoring axes, every number
4. **`BENCHMARKS.md`** — internal suite plus the external scoreboard
5. **`PRIOR_ART.md`** — incumbent stacks and their documented limits
6. **`COMPARISONS.md`** — head-to-head, including where comparators lead
7. **`docs/ARCHITECTURE.md`** — design, ideate → innovate → design → test → build

## Axioms

**A1** zero float (statically linted) · **A2** reconstruction-free — no Garner,
no mixed-radix, magnitude by K-Elimination · **A3** distortion certified, trivial
here (Γ = 1) · **A8** no Sqr on lane 7, enforced by refusal · **DKAM** ρ = 3 > d = 2 ·
modular inverses by extended Euclid only, never Fermat.

## Current target

The Archimedes Palimpsest folios bearing 20th-century forged Evangelist
portraits, where the incumbent optical stack recovers nothing and the project
escalated to synchrotron XRF. Data is acquired and checksummed; the run is open.
Result will be reported at whatever size the evidence supports, including zero —
see `BENCHMARKS.md` §2.

---

Data under `data/` derives from the Archimedes Palimpsest release (CC BY 3.0).
Framework code © Anthony Diaz; private repository.
