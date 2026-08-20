# CRAM-DSP

**Digital signal and image processing with no floating point, anywhere.**
Every number is an exact integer. Every transform is reversible. Every run
proves, by hash, that it did exactly what it says — twice, bit for bit.

Built by Anthony Diaz (Acid), HackFate Research / Skyelabz210, on the CRAM /
QMNF residue-arithmetic framework.

```
2,585,391 exact checks   ·   0 failures   ·   A1 lint PASS
```

---

## The problem this exists to fix

Every standard image-processing pipeline — blur, enhancement, layer
separation, convolution — runs on floating point, and floating point is not
exact. It rounds. It drifts. It depends on which chip and which library
version happened to run it. When the input is *evidence* — a forged
manuscript, a spliced photograph, an undertext buried under paint — that
rounding isn't a footnote, it's a loss with no receipt: nothing tells you
afterward what got destroyed. Measured on a page of test evidence in this
repo: one ordinary float blur destroyed 26 of 114 marked ink edges,
manufactured 682 detections that were never there, and erased all 28 of the
page's processing-history fingerprints. Permanently. Silently. That isn't a
bug in one blur filter — it's what floating point does to exact structure,
by construction, every time it's used.

CRAM-DSP is what the same class of operations looks like with the float
removed entirely — not approximated better, removed.

## How it actually works

Residue arithmetic — splitting a number into its remainders under several
small moduli and computing on each remainder independently — has existed for
decades, and it's fast: addition and multiplication run in parallel across
the "lanes" with zero rounding, ever. Its one long-standing weak point was
*getting the size back out*. To answer "how big is this number," the
classical approach has to glue every lane back into one positional number
(Garner's algorithm and its relatives) — slow, and worse, it makes every
lane's value depend on all the others, destroying the very independence that
made the fast parallel arithmetic worth having.

**K-Elimination removes that step.** The magnitude — the exact overflow
count, the exact band a value falls in, the exact winding number — comes out
of a single modular subtraction between two lanes. No gluing. No dependence
between lanes. It's a five-line proof (`PROOFS.md`, P1), not a heuristic, and
almost everything downstream of it — exact banding, the residue-native edge
probe, exact layer separation, the reversible transforms — is just that one
theorem applied to a different problem.

## Where this is being tested right now

Four folios of the Archimedes Palimpsest carry 20th-century forgeries — gold
leaf and pigment painted directly over the original Archimedes text. The
multispectral imaging system built for this exact manuscript — later adopted
by the Library of Congress, the Dead Sea Scrolls project, and Sinai — was
pointed at those folios and **recovered nothing**. The team had to fly the
leaves to the SLAC synchrotron and read the iron in the ink with X-rays
instead.

CRAM-DSP hasn't touched the undertext yet — that run is open, and it will
report whatever it finds, including zero. But on first contact with the raw
sensor files, before any of that work even started, its own integer
fingerprint check found something the standard optical pipeline has no way
to see: across 70,350,000 sample values, the published "16-bit" release is
secretly 14-bit sensor data padded into a wider container, with zero
exceptions. Every tool that's ever touched this public dataset has been
reporting two bits of padding as real precision. That's the target this
framework is now running against — tracked live in `BENCHMARKS.md`.

## What's been measured so far

| Claim | Evidence |
|---|---|
| Exact layer separation where the mixing operator is rational | 0 error vs float PCA's MAE 2.296 / 4.899 on identical input |
| Exact stratification without decoding magnitude | `floor(L/M)` from a residue pair, exhaustive at 8- and 16-bit |
| Detection with the full-width image absent | identical 114/114 map computed from lane trays alone |
| CRT alias rejection | Δ=12 confounder that fools a single lane rejected by the comb; Δ=11 blind spot closed |
| Evidence survives processing | 114/114 edges and 28/28 fingerprint blocks after round trip; float path loses all |
| Reproducibility | identical chain hash across independent runs |
| Real-artifact finding, first contact | the Archimedes release is 14-bit data in a 16-bit container — 70,350,000 values, 0 exceptions |
| Real-artifact survivability | float blur keeps 25.136% of the lattice and 1,182/2,513 unit steps; exact path keeps 100% and 2,513/2,513 |
| Real-artifact reproducibility | identical chain hash across independent runs on Archimedes data |
| Board 1 (forged folios) | **shipped negative** — no undertext claim; incumbent needed a synchrotron and this run does not beat one |

Every one is scoped in `METRICS.md` and proved in `PROOFS.md`. Where a result
overlaps existing methods, the axis, conditions, and location of the
differentiation are stated — see `COMPARISONS.md`. Nothing above is a bare
"beats the incumbent" claim; every row names what's actually being compared.

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

## Execution

The live campaign plan is **`EXECUTION_DAG.md`** (52 gated nodes, all target
boards); agent rules are in **`CLAUDE.md`**; the append-only session record is
`docs/executioner_dag.md`.

## Read in this order

1. **`MANIFEST.md`** — full inventory, every file and its gate
2. **`PROOFS.md`** — P1–P13, each with proof and its witnessing test
3. **`METRICS.md`** — measurement contract, six scoring axes, every number
4. **`BENCHMARKS.md`** — internal suite plus the external scoreboard
5. **`BOUNTIES.md`** — live prize targets with gate-by-gate clearance audit
6. **`PRIOR_ART.md`** — incumbent stacks and their documented limits
7. **`COMPARISONS.md`** — head-to-head, including where comparators lead
8. **`docs/ARCHITECTURE.md`** — design, ideate → innovate → design → test → build

## The rules that hold it together

- **A1 — zero float.** Every production number is an exact integer or exact
  fraction. Statically checked on every run: the linter fails the build if a
  float slips into a real code path. (Comparison foils are quarantined by
  name specifically so they can be float — that's the point of having them.)
- **A2 — no reconstruction.** Magnitude is never recovered by gluing all the
  residue lanes together (Garner / mixed-radix). K-Elimination reads it off
  two lanes, as above.
- **A3 — distortion is certified, not assumed.** The rare non-standard lane
  operator has to carry an exact certificate of what it distorts; on every
  production path here that certificate is trivial (Γ = 1) because the
  operators are plain arithmetic homomorphisms.
- **A8 — the one operator that isn't gets refused, not warned about.** `Sqr`
  is disallowed outright on lane 7; the call raises rather than logging a
  warning.
- **DKAM.** The nonlinear operator's degree (2) stays under the basis's
  resonance order (3) — the condition that keeps repeated operations from
  blowing up instead of staying bounded.
- **Inverses.** Always extended Euclid, never Fermat's little theorem — Fermat
  is silently wrong on the composite moduli this framework uses on purpose.

## Licence

Framework code, tooling, and the `dsp-analyst` skill: **MIT** (`LICENSE`).
Documentation and research records: **CC BY 4.0**. Data under `data/` derives
from the Archimedes Palimpsest release (**CC BY 3.0**), redistributed with
values unmodified. Full attribution and rationale in `NOTICE.md`.
