# Machine status — what is validated, what is still being built

Governed by `docs/RULES_OF_EXPLORATION.md`. This file answers one question:
**which parts of the machinery are trustworthy enough for the researcher's
exploration to lean on, and which are not yet.** No hypothesis is marked
closed anywhere in this repo, and none may be while stages remain unvalidated.

Status vocabulary: **VALIDATED** (fixtures + controls pass, failure modes
known and receipted) · **BUILT, UNVALIDATED** (runs and produces exact
numbers; its controls are not yet designed or not yet passing) ·
**NOT BUILT**.

## Stage table

| Stage | What it does | Status | Controls that back it |
|---|---|---|---|
| Ingestion (DRE-01) | 78 scans byte-exact, receipted, characterized | **VALIDATED** | blank-page positions predicted by the Förstemann mapping land exactly on the four measured near-blank scans |
| Localization | finds a photograph's place in the codex | **VALIDATED** | positive control (known crop → own page, exact offset), per-query null over 78 pages, blank-page null for the same template, hard negative named, abstention on thin margins |
| Glyph codes (ring + dihedral sector) | per-glyph internal signature, pose-aware | **VALIDATED** | exact invariance fixtures (mirror/rot90/rot180 = 0 on asymmetric shapes), bar-vs-dot separation, pose tally reported against its chance baseline |
| Pigment / shadow lenses | exact 4-way chroma partition; dark-end freeze | **VALIDATED** | fixture classes exact; fractions sum to 1000 |
| Dot morphology | open vs filled round marks, unlabelled | **VALIDATED** | topology fixture; both classes populated; separation reported with overlap figures rather than asserted |
| White nodes (evidence records) | contrast, gradient direction, chroma, score | **VALIDATED** | neutral-vs-warm fixture: an equally bright warm mark must not outscore a neutral one |
| Path agreement (3 constructions) | brightness / spatial / gradient-flow orderings | **BUILT, UNVALIDATED** | agreement is computed exactly, but no control yet distinguishes "the page has an ordering" from "any three constructions over any node set agree this much". **A null over reshuffled node positions is the missing piece.** |
| White trails (filaments) | continuous gradient-to-white streaks | **BUILT, UNVALIDATED** | trails are extracted exactly and their glyph sequences are exact, but no control yet separates a designed trail from fiber, sizing, or plaster loss. **Materials evidence or multi-illumination capture is the missing piece.** |
| Cross-page trail continuity | facing-edge alignment between scans | **BUILT, UNVALIDATED** | 96 alignments measured; the null (how many alignments arise between unrelated page pairs) is **not yet computed** — until it is, the number is a measurement without a scale |
| Radial character decomposition | centre-outward rings/sectors, per-pose matching | **BUILT, UNVALIDATED** | matches are exact and poses are separated, but match *significance* has no null yet; distances are large at this scan resolution |
| Light activation | illumination-dependent behaviour | **NOT BUILT** | requires RTI / multispectral capture of the physical object; not testable on fixed-illumination scans |

## The two failures this build cycle, kept as receipts

1. **Score comparability.** The localizer's raw co-occurrence score scaled
   with each window's own edge mass, so scores from different templates were
   not comparable — the control battery surfaced it as a "texture floor"
   (2380) sitting above the real query (826 on the same nominal scale).
   Replaced by an exact integer cosine, Cauchy-Schwarz-bounded to 1000.
2. **Control design.** The first battery compared *a different template's*
   best score against the main query's score, which is meaningless. The
   per-query null (this template's score across all 78 pages, and on the
   blank pages specifically) replaced it. Both failures are recorded in the
   code that fixed them.

A third, older failure — the median-centred luma SAD false negative — keeps
its full provenance chain in `DRESDEN_MACHINE.md` §C4.

## What the machine currently measures (all MEASURED, no verdicts)

- The photographed column is at scan 73 / Förstemann p69 / x 64–274 /
  y 772–1350: cosine 826, median over pages 685, best blank-page score 709,
  rank percentile 1000/1000, hard negative named.
- White nodes in **written zones** carry higher local contrast than nodes on
  **bare substrate** on every page where both exist (18/13, 16/12, 29/12,
  21/19), with larger spacing — the two zones are not interchangeable under
  the same algorithm.
- **96** facing-edge trail alignments between consecutive scans (null still
  to be computed).
- Open round marks are a larger, thicker population than filled ones
  (median area 98 vs 39; thickness 1510 vs 1000; only 325/1000 of open marks
  fall inside the filled interquartile range on area).
- Radial decomposition of the p69 character yields 31 pieces in ring/sector
  coordinates; the pose tally (4 direct / 14 rotated / 3 mirrored /
  10 rot+mir) sits essentially at its 1:3:1:3 multiplicity baseline.

## What must be built before exploration leans on the trail hypothesis

1. A null for path agreement (reshuffled node positions, same page).
2. A null for cross-page continuity (alignments between non-adjacent pages).
3. A trail-vs-materials discriminator, or the acknowledgement that this
   needs physical-object evidence.
4. Higher-resolution captures: at 684×1350 the glyph codes are
   under-resolved for complex interiors, which bounds every matching result.
