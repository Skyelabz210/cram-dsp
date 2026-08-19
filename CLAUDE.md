# CLAUDE.md — agent instructions for this repo

CRAM-DSP: residue-native forensic DSP. Exact integers end to end, reversible
transforms, hash-chained provenance. Owner: Anthony Diaz (Skyelabz210).

## The plan and the record

- **`EXECUTION_DAG.md`** (repo root) is the campaign plan: 52 gated nodes.
  Work it in dependency order. One node at a time.
- **`docs/executioner_dag.md`** is the append-only session record. Append node
  completions and checkpoints there. NEVER overwrite or rewrite it.
- `MANIFEST.md` is ground truth for what exists. Read it before writing
  anything. If an output already exists: mark the node SKIP-EXISTS and wire to
  the existing file.

## Hard rules (violations are build failures, not style issues)

1. **A1 — zero float on production paths.** Only `//`, `%`, `>>`, integer
   numpy dtypes. `cram_dsp/baseline_float.py` is the ONLY float file
   (quarantined comparison foils). Run `python3 cram_dsp/a1_lint.py cram_dsp`
   before marking any node done. If a task seems to need float, STOP and flag
   it in the DAG — do not approximate.
2. **A2 — no Garner, no mixed-radix, no positional decode.** Magnitude comes
   from K-Elimination (`core.DualTrack`, `core.tower_k`) — one modular
   subtraction (+ one multiply off the adjacent pair). `derive()` is an
   emission seam only.
3. **Modular inverses: `pow(a, -1, m)` (extended Euclid) ONLY.** Never
   `pow(a, m-2, m)` — Fermat is silently wrong on composite/anchor moduli.
4. **A8 — never apply Sqr on lane 7.** `core.sqr_carry` refuses it; keep it
   that way.
5. **Nothing is generated.** No inpainting, no synthesis of evidence values.
   Every emitted value must be an exact function of input integers; renders
   sample by nearest neighbor (see NODE-INF07 geometry-cast rule).
6. **Receipts.** Every acquisition and every transform on evidence goes
   through `forensics.Ledger`. External data gets URL + byte range + SHA-256.
7. **Negative results ship.** A zero is reported as zero
   (`BENCHMARKS.md` §3). Never inflate; never bury.
8. **Scoped reporting.** Where a measurement overlaps an existing method:
   name the axis, the exact conditions, and where the differentiation lives —
   never a bare "on par" verdict.

## Gates (every node)

G1 outputs at stated paths · G2 `a1_lint` PASS + float grep clean ·
G3 `python3 -m py_compile` (or `cargo check`) clean · G4 tests pass ·
G5 the node's own gate in EXECUTION_DAG.md · G6 axiom quick-check (A2, A8,
inverse guard). "It should work" is not a gate — run it.

## Commands

```bash
python3 run_all.py                      # full T-suite -> demo/RESULTS.md (must stay 0 failures)
python3 cram_dsp/a1_lint.py cram_dsp    # A1 static compliance
python3 tools/fetch_tiff.py <folio> <band> <r0> <nrows> <c0>:<c1>   # Archimedes crops
```

Baseline to protect: **2,585,391 checks, 0 failures.** New tiers may grow the
count; nothing may shrink it or fail.

## Data discipline

Large binaries stay out of git (`.gitignore`); pin them in `data/SHA256SUMS.txt`
and make them regenerable by a receipted tool. Commit fixtures only when small
(like `data/archimedes_caltarget.npz`).

## Token boundary

Approaching the context limit: finish the current node if within 2–3 edits,
append a checkpoint (completed / in-progress / next-step / pending) to
`docs/executioner_dag.md`, commit, push, stop. A clean partial beats a
corrupted complete.

## HUMAN-gated nodes

VES-06 (licence/public flip), VES-07 (Discord + submission form), GPZ-04
(segmentation-path decision), SEL-02 (Bodleian outreach), SIN-01 (UCLA
registration), DRE-01 input (scan set). Do not fake these; mark BLOCKED with a
`Requires:` line and move to a parallel track. Deadline that matters:
**Progress Prize 2026-08-31 23:59 PT** (Track 1 in EXECUTION_DAG.md).
