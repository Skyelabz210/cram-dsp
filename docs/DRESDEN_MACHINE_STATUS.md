# Machine status — what is validated, what is still being built

Governed by `docs/RULES_OF_EXPLORATION.md`. This file answers one question: **which instruments are built, and what
each one's numbers can be read against.** There is no verdict horizon here
and nothing to lean on — exploration does not accumulate toward a ruling.
A stage marked unvalidated is not a stage awaiting permission; it is an
instrument whose readings do not yet have a scale.

Status vocabulary: **VALIDATED** (fixtures + controls pass, failure modes
known and receipted) · **BUILT, NO SCALE YET** (runs and produces exact
numbers, but nothing yet says what those numbers compare against) ·
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
| Path agreement (3 constructions) | brightness / spatial / gradient-flow orderings | **VALIDATED (scale S1 built)** | shuffled-position scale: positions permuted, all node attributes kept. 70 of 78 pages sit inside the shuffled range; 8 sit above every shuffle (p14, p19, p28\*, p29, p51, p52, p59, p74) |
| White trails (filaments) | continuous gradient-to-white streaks | **BUILT, NO SCALE YET** | trails are extracted exactly and their glyph sequences are exact, but no control yet separates a designed trail from fiber, sizing, or plaster loss. **Materials evidence or multi-illumination capture is the missing piece.** |
| Cross-page trail continuity | facing-edge alignment between scans | **VALIDATED (scale S2 built)** | consecutive scans 1246 alignments-per-1000-pairs (40/77 pairs align); non-adjacent sample 810 per 1000 (75/200 pairs) |
| Radial character decomposition | centre-outward rings/sectors, per-pose matching | **BUILT, NO SCALE YET** | matches are exact and poses are separated, but match *significance* has no null yet; distances are large at this scan resolution |
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
- **96** facing-edge trail alignments across 77 consecutive scan pairs
  (1246 per 1000 pairs; 40 of 77 pairs align), against **162** alignments
  across a 200-pair non-adjacent sample (810 per 1000; 75 of 200 pairs).
- Path-agreement on **8 of 78** pages exceeds every shuffled-position
  arrangement of the same nodes (p14, p19, p28\*, p29, p51, p52, p59, p74);
  the other 70 sit inside the shuffled range.
- Open round marks are a larger, thicker population than filled ones
  (median area 98 vs 39; thickness 1510 vs 1000; only 325/1000 of open marks
  fall inside the filled interquartile range on area).
- Radial decomposition of the p69 character yields 31 pieces in ring/sector
  coordinates; the pose tally (4 direct / 14 rotated / 3 mirrored /
  10 rot+mir) sits essentially at its 1:3:1:3 multiplicity baseline.

## Instruments still to build (scales, not gates)

Each of these gives an existing measurement a scale to be read against. None
of them authorizes a conclusion, and none of them can close anything.

1. ~~Path-agreement scale~~ — **built** (`analysis/dresden_scales.py` S1).
2. ~~Continuity scale~~ — **built** (S2).
3. **Trail-vs-materials discrimination** — needs physical-object or
   multi-illumination evidence; no scan-side instrument can supply it.
4. **Higher-resolution capture** — at 684×1350 the glyph codes are
   under-resolved for complex interiors, which bounds every matching
   number currently produced.
