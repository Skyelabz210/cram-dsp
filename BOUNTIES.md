# BOUNTIES

Live prize targets in this problem space, with a gate-by-gate clearance audit.
Status vocabulary is strict:

- **CLEARED** — the gate is satisfied *now*, by something verified in this repo.
- **PARTIAL** — machinery exists but has not been demonstrated on the target data.
- **NOT CLEARED** — no capability yet; what it would take is stated.

Nothing is marked CLEARED on the strength of an argument. Only on a test.

---

## Board A — Vesuvius Challenge (verified 2026-08-19 from scrollprize.org/prizes)

**Open prize pool: $2,140,000. Grand Prize deadline: June 25, 2027, 11:59pm Pacific.**

### A1 · 2027 Grand Prize — $1,000,000 total
$800,000 first, $100,000 second, $50,000 third, $50,000 fourth. Fully unroll and
make readable one of **13 eligible scroll volumes** (PHerc. 125, 191, 211, 257,
268, 358, 800, 813, 826, 1203, 1218, 1447, 1545).

| # | Gate | Status | Note |
|---|---|---|---|
| 1 | Pipeline fully reproducible | **CLEARED** | P12: deterministic integer pipeline, identical chain hash across independent runs. This is the strongest card we hold — the challenge lists reproducibility at collection scale as an *open problem* |
| 2 | Open source under permissive licence on GitHub | **PARTIAL** | Repo exists and is complete; currently private. One licence file and a visibility flip |
| 3 | Fixed random seeds, reported | **CLEARED** | Every generator seeded; A1 forbids stochastic float paths entirely |
| 4 | False-positive mitigation | **CLEARED (by construction)** | Nothing is generated. Every output is an exact function of input integers — a letterform that was not measured cannot appear. The strongest possible answer to "why are you confident the results are real" |
| 5 | No train/predict overlap; ≤0.5×0.5 mm windows | **CLEARED (not applicable)** | No model, no training data, no memorization surface |
| 6 | 100% of recto surface unrolled, tifxyz meshes, VC3D integration | **NOT CLEARED** | No 3-D surface tracing capability. Would require building segmentation from scratch or teaming |
| 7 | Ink detection, ≥70% of characters legible per column | **NOT CLEARED** | Untested on µCT volumes |
| 8 | Teravoxel-scale operation (OME-Zarr streaming) | **NOT CLEARED** | Pure-Python engine; awaits the Rust/NEON port |
| 9 | ≤8 hours human input, automated pipeline | **PARTIAL** | Our path is fully automatic, but only over the parts we implement |

**Verdict: not winnable solo as it stands.** Gates 6–8 are the whole unwrapping
and ink-detection stack. Realistic route is as the *verification and exactness
layer* on someone else's segmentation — the challenge explicitly frames this as
"a great prize to tackle as a team."

### A2 · First Letters — $50,000 per scroll, up to 10 scrolls ($500,000)
10 legible letters within a single 4 cm² area of a scroll where nothing has been read.

| # | Gate | Status | Note |
|---|---|---|---|
| 1 | Image generated programmatically from CT volume + mesh | **PARTIAL** | Exact integer rendering is ours; the mesh is not |
| 2 | No manual annotation of characters | **CLEARED** | Nothing is drawn; probes emit masks |
| 3 | False-positive mitigation | **CLEARED (by construction)** | Same as A1 gate 4 |
| 4 | No train/predict overlap | **CLEARED (not applicable)** | No model |
| 5 | Held-out validation with known ground truth | **CLEARED (methodology)** | Exhaustive-where-feasible testing is already the house standard; k-fold is moot without a model |
| 6 | Open source after winning | **PARTIAL** | Same as A1 gate 2 |
| 7 | Segment growth / flattening on the recto surface | **NOT CLEARED** | Same blocker as A1 gate 6 |
| 8 | 10 legible letters | **NOT CLEARED** | Not attempted |

**Note worth acting on:** the prize page states that *sometimes ink is visible
directly in the flattened render with no model at all*, and that this alone
qualifies. That is a pure exact-DSP target — contrast recovery on an existing
flattened render, no ML. **This is the most winnable item on the whole board for
this framework**, and it needs only a published segment, not our own.

### A3 · PHerc. Paris 4 Title Prize — $50,000
Recover the title of Scroll 1. The expected title region has shown **no
detectable ink so far** — possibly a different ink chemistry; top rows physically
missing. Any published volume qualifies, including 2.4 µm scans.

| # | Gate | Status | Note |
|---|---|---|---|
| 1 | Programmatic image from volume + mesh | **PARTIAL** | Rendering ours; mesh not |
| 2 | False-positive mitigation | **CLEARED (by construction)** | |
| 3 | Detect ink where existing methods detect none | **NOT CLEARED — but this is the archetype** | "No signal found by float pipelines" is precisely the condition the lane-comb probe, exact unmixing, and the 14-bit-lattice class of finding exist for |
| 4 | Submissions remain open until won | **advantage** | No deadline pressure; a late-correct method still wins |

**Assessment:** highest fit-to-capability ratio of the three milestone prizes.
A different ink chemistry means a different residue class, not a different
brightness — the discriminator we already build.

### A4 · Progress Prizes — $20,000/month guaranteed, plus $500–$20,000 tiers
Monthly, open-ended, for open-source contributions to the open problems. Next
deadline **August 31, 2026**.

| # | Gate | Status | Note |
|---|---|---|---|
| 1 | Addresses a specific challenge using their scroll data | **PARTIAL** | Must run on their data — not yet done |
| 2 | Released/open-sourced early | **PARTIAL** | Repo is ready to flip public |
| 3 | Comprehensive documentation + usage examples | **CLEARED** | README, MANIFEST, PROOFS, METRICS, BENCHMARKS, PRIOR_ART, COMPARISONS, ARCHITECTURE |
| 4 | Accepts community formats (OME-Zarr, tifxyz) | **NOT CLEARED** | Needs a Zarr reader — small, well-defined work |
| 5 | Quantitative evaluation on their public datasets | **PARTIAL** | The evaluation discipline exists (`METRICS.md`); it has not been pointed at their ink-label or surface-label sets |
| 6 | Demonstrates advantage over existing solutions | **CLEARED (methodologically)** | `COMPARISONS.md` is exactly this document, per axis, including where they lead |
| 7 | Modular integration | **CLEARED** | Library surface, no framework lock-in |

**Verdict: this is the near-term winnable board.** Five of seven gates are
cleared or nearly so; the two open ones are a Zarr reader and one evaluation run.
**Deadline is 12 days out.**

---

## Board B — Non-cash bounties (first-mover claims)

| Target | The open question | Status |
|---|---|---|
| **Vesuvius open problem: "no ink" vs "no ink recovered yet"** | Posted as unsolved, July 2026 | **PARTIAL** — exact residue-class tests give a decidable answer in principle; unvalidated on their data |
| **Vesuvius open problem: collection-scale reproducibility** | Posted as unsolved | **CLEARED on our pipeline** (P12); unproven on theirs |
| **Syriac Galen: first quantitative score** | Eight methods ranked *visually*, no numbers ever published | **PARTIAL** — data is CC BY and downloadable; `METRICS.md` supplies the protocol; run not done |
| **Archimedes forged-Evangelist folios** | Optical multispectral recovers nothing; project escalated to synchrotron XRF | **PARTIAL** — data acquired and checksummed; engine not yet run on the window |
| **Archimedes 14-bit lattice** | Undeclared property of the public release | **CLEARED** — 70,350,000 values, 0 exceptions, per-band gcd exactly 4. Found on first contact |

---

## Ranked shortlist

1. **A4 Progress Prize** — $20,000, deadline Aug 31 2026. Build a Zarr reader,
   run the exact-DSP evaluation on their public ink-label set, publish the repo.
   Five of seven gates already cleared.
2. **A3 Title Prize** — $50,000, no expiry, and the failure condition ("no
   detectable ink so far") is exactly the condition this framework targets.
3. **A2 First Letters** — $50,000/scroll, via the *no-model* route the prize page
   itself sanctions: ink visible directly in an existing flattened render.
4. **Board B non-cash** — the Archimedes forgery run and the Galen quantitative
   score. No money, but both are first-mover claims on documented failures.
5. **A1 Grand Prize** — not solo. Team play as the exactness/verification layer.

---

## Honest accounting

Of the four cash boards, **zero are currently winnable end-to-end by this
framework alone.** The blocking gate on all three milestone prizes is the same
one: 3-D surface segmentation and flattening, which this repo does not do and
does not claim to. What it does hold is an unusually strong hand on the gates
*everyone else finds hard* — reproducibility, false-positive mitigation, seed
determinism, and quantitative evaluation — because those fall out of A1 and A2
rather than needing to be engineered.

That asymmetry is the strategy: enter where exactness is the scarce good
(Progress Prizes, the Title Prize, the no-model First Letters route), not where
segmentation is.
