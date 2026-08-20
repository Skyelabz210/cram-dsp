# NOTICE — licensing and attribution

## Framework code — MIT

`cram_dsp/`, `run_all.py`, `analysis/`, `tools/`, and `skills/dsp-analyst/`
are licensed under the MIT License (see `LICENSE`). Copyright © 2026
Anthony Diaz (HackFate Research).

MIT was chosen deliberately: it is permissive, it is the licence the Vesuvius
Challenge names as acceptable for prize eligibility ("open source under a
permissive licence, publicly on GitHub"), and it imposes no obligation on
downstream heritage institutions that may want to adopt the exact-arithmetic
pipeline. If a different licence is preferred (Apache-2.0 for its explicit
patent grant, or a dual arrangement), replacing `LICENSE` is the only change
required — nothing in the codebase depends on the licence text.

## Documentation and research records

The written record — `PROOFS.md`, `METRICS.md`, `BENCHMARKS.md`,
`BOUNTIES.md`, `PRIOR_ART.md`, `COMPARISONS.md`, `EXECUTION_DAG.md`, and
everything under `docs/` — is © 2026 Anthony Diaz, released under
Creative Commons Attribution 4.0 (CC BY 4.0). Cite as:

> Diaz, A. (2026). *CRAM-DSP: residue-native forensic digital signal and
> image processing.* HackFate Research.

## Third-party data

`data/archimedes_*.npz` and anything derived from them originate in the
Archimedes Palimpsest digital release, published under **CC BY 3.0**.
Attribution: the Owner of the Archimedes Palimpsest, with imaging by
W. A. Christens-Barry, R. L. Easton Jr., and K. T. Knox. Source mirror:
`mirrors.rit.edu/archie/`. These files are redistributed under that licence,
unmodified in value: the acquisition path performs no resampling or
transcoding, so the integers on disk are the integers the imaging team
published.

Vesuvius Challenge datasets, when acquired under `data/vesuvius/`, carry
their own terms (generally CC BY-NC 4.0 for challenge-derived datasets) and
are not covered by this repository's licence.

## Patent and prior-art position

Nothing here is filed. The mathematical results in `PROOFS.md` are published
openly in this repository with dated commits, which establishes prior art and
keeps the constructions freely usable.
