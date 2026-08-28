# Icon → character correspondence by exact geometric registration — page 47

Run: `python3 analysis/dresden_correspond.py 50`.
Receipts: `data/dresden/correspond_receipts_47.json`; full per-pair record
`data/dresden/correspond_47.json`.
Visuals: `demo/dresden_correspond_sheet_p47.png` (page sheet) and 24 labelled
overlays in `demo/correspond/`.

Status vocabulary per `docs/RULES_OF_EXPLORATION.md`: everything below is
MEASURED. Nothing is closed, and nothing here is a verdict on the
researcher's hypothesis — it is a statement about what this instrument, at
this resolution and with this segmentation, currently reads.

## What was run

Förstemann page 47 (scan 50), a Venus-table page with framed picture panels.

- **Characters**: 2 detected as large black-ink drawings — y242-568 x379-582
  and y710-1011 x325-594. Red register rules are excluded by construction;
  with them included the whole page merges into one component.
- **Icons**: 56 — every glyph/icon form on the page outside both character
  boxes, at least 16 px on each side, area ≥ 150, and carrying interior
  structure (fill < 780 milli or ≥ 1 enclosed hole). None skipped.
- **Registrations**: 56 icons × 2 characters × 2 spaces (ink and negative
  space) = **224**, all computed.
- **Transform ladder**: translation → exact rational rotation (Pythagorean
  triples) → exact rational uniform scale ∈ {2/3, 3/4, 1/1, 4/3, 3/2},
  mirror on/off. No anisotropic or affine warping. Coarse search at quarter
  resolution over the whole character, then a full-resolution exact IoU map
  over every placement; that single map yields both the best placement and
  its matched null.

## Results

### The dominant reading is an artifact of my own search, not the page

**194 of 224 matches chose scale 2/3 and 29 chose 3/4 — only one chose 1/1.**
Essentially every fit went to the smallest scale the ladder allowed. Shrinking
an icon raises IoU mechanically, so the objective is biased toward the edge of
the band. Until the objective is made scale-neutral, the fitted scales are not
evidence of anything about the page.

**223 of 224 chose rotation 0°.** Rotation is contributing nothing at present;
the fits are axis-aligned translations plus shrink.

### The margin statistic I first reported is worthless — retracted

The run reports every pair "beating its own 95th-percentile placement"
(224/224). That is **trivially true by construction**: a maximum always
exceeds the 95th percentile of the same distribution. It is not evidence and
it is withdrawn as a statistic. The comparisons that can carry information are
the cross-panel one and the topology gate, below.

### Cross-panel control: no panel specificity

If an icon corresponded to a feature of *its own* character, it should fit
that character markedly better than the other one. Measured over the 56 icons
tested against both characters:

- character 0 preferred by **21 of 56** icons (37%) — close to a coin flip
- median |IoU(char 0) − IoU(char 1)| = **26 milli**; maximum 136 milli

Icons fit both characters about equally well. That is what the control was for.

### Topology gate: 20 of 224

Requiring endpoint and branch-point counts to agree — the strict reading of
"exact" — **20 of 224 registrations pass, 204 fail**. By that definition no
correspondence on this page is established.

### Location reuse (measured, uninterpreted)

Normalised character coordinates do show clustering: on character 0, 7 icons
land in the same 100-milli cell (x 500-600, y 0-100) and 7 more in
(x 600-700, y 0-100); on character 1, 6 icons land in (x 600-700, y 600-700).
Whether that is structure or simply the densest ink regions attracting every
placement is not separable with the current objective.

## Why the instrument may be under-powered

Stated so the next build targets the right things, not as excuses:

1. **Scale bias** — the objective rewards shrinkage. Needs a scale-neutral
   score (e.g. agreement per unit icon area, or a penalty tied to the scale
   deviation from 1).
2. **Character segmentation** — these Venus figures are *polychrome
   paintings*, not line drawings. The mask being registered against is a
   luma/pigment threshold of a painted surface, so it is not the drawn line
   work the hypothesis is about. Extracting the outline drawing beneath the
   colour is a prerequisite.
3. **Resolution** — 684×1350 per page. A 16 px icon carries very little
   interior once transformed; contour precision is bounded by the scan.
4. **IoU on dense art** — area agreement was chosen because chamfer
   saturated (see receipts below), but IoU still favours blobs over
   structure.

## Failed methods kept as receipts

1. **Chamfer-to-EDT objective.** One-directional chamfer against a character's
   contour saturates: a character is a dense line drawing, so every small icon
   sits within a pixel of *some* stroke. The null control caught it — random
   crops scored a perfect 0 mean distance. Replaced by exact area agreement.
2. **Size-mismatched null.** The first null used random page crops, which are
   smaller and sparser than real icons and therefore scored higher by being
   tiny. Replaced by the matched null (same icon, same character, every other
   offset) — which then turned out to be trivially satisfied, as recorded
   above.
3. **Resolution-mismatched null.** A full-resolution best was briefly compared
   against a quarter-resolution null. Both now come from one full-resolution
   map.
4. **Fragment icons.** Sub-16 px fragments let the search win trivially
   (a 9-px blob registers onto any 9-px blob); the first overlay pass exposed
   it and the filter was added.

## Reproduce

```bash
python3 analysis/dresden_correspond.py 50          # full page, all icons
python3 analysis/dresden_correspond.py 50 --fast   # every 4th icon
```
