# p17 (scan 17) — icon-to-character exact geometric registration

Page chosen by the researcher: *"Do page 17 of 78, I definitely see this
page."* It is the concept illustration's layout made literal. Unlike p47
(polychrome paintings inside bounded panels) or p69 (one figure beside a
text column), here the small oval icons float in the **same open field** as
the figures — above, below and between them — which is the arrangement the
illustrations depict.

Governed by `docs/RULES_OF_EXPLORATION.md`. Order is fixed and was not
reversed: **geometry → recurrence → significance → interpretation.** This
report stops at significance. No meaning is assigned to any element, and
**nothing here is closed** — every number below is a statement about the
INSTRUMENT, not about the researcher's hypothesis.

Run: `python3 analysis/dresden_p17.py` then
`python3 analysis/dresden_p17_report.py`.
Visuals: `demo/dresden_p17_inventory.jpg`, `demo/dresden_p17_overlays.jpg`,
per-registration overlays in `data/dresden/derived/p17/overlays/`.

## 1. How the page is decomposed

New production primitive: **`cram_dsp.dresden.local_dark_field`** — per-pixel
darkness below the *local* substrate level, where the substrate level of each
24×24 block is the lower-quartile luma of that block's non-ink pixels. It is
an EVIDENCE transform, not an enhancement: every selected pixel is genuinely
darker than the measured surface around it, by a stated margin. Nothing is
brightened or interpolated.

It exists because of a measured failure. The figures on p17 are drawn in a
much finer line than the icons, and **global Otsu misses them completely** —
under the previous detector this page's five "figures" were all blocks of
*writing*, and not one of the four real figures was found.

Then three further attempts at separating icon from figure, all kept:

| # | Method | What happened |
|---|---|---|
| a | Second global Otsu threshold | The band between the two cuts is **323/1000 of the page** — it selects shaded plaster too. Line and shading do not separate against a global reference. |
| b | Remove heavy ink from the dark field | **Destroys the figures** (fine fill → ~0/1000). The figure line is not *lighter* than the Otsu cut. Brightness was the wrong axis. |
| c | Stroke width (opening by radius 2) | Separates figure from *writing*, but not figure from *icon*: the ovals are thin-outlined rings, so the opening erased them too and the only "icons" returned were the solid fills inside the figures (a headdress, a waistband). |

What separates them is **topology**. Each oval is a small **closed loop**;
the figure line is a large open structure. Measured at dilation zero:
**67 compact components carry a hole, median 34×41 px**, against 6 large
structures.

Result: **67 icons, 10 targets**, disjoint *by component identity*.

## 2. The self-matching defect this run found (receipt)

An intermediate version took targets as the thin-stroke components and icons
from the segmentation cells. The ovals are thin, so after dilation **they
joined the figure's component** and every target silently contained the icons
that surround it.

That run's top result — icon 32 → T5, **IoU 547, boundary overlap 982/1000**
— is visibly, in its own overlay, the icon landing on the edge of a
**neighbouring oval, outside the figure entirely**. The icon set was
registering onto itself. It was caught by looking at the picture, not by any
score.

A follow-up fix (cut every segmentation cell out of the targets) failed the
other way: on this page the cell pass also boxes parts of the figures, so it
shredded all four figures below the size floor and left only writing.

## 3. The statistic that is NOT reported as a result (receipt)

The first complete run reported that **608 of 608** ink registrations
"cleared their own matched null" — 76 of 76 on every single target. That is
close to a tautology: the matched null is the IoU distribution of the *same*
icon over every offset on the *same* target, and the argmax of a distribution
beats its own p99 unless the top percentile is flat. It measures nothing
about correspondence.

In the final runs the same degenerate count is **670 of 670**. It is carried
in the summary only so the degeneracy stays visible. The same defect was
already receipted once on p47; the rewritten pipeline reintroduced it, which
is exactly why it is written down here again.

## 4. The control that does mean something

Icons drawn on a **different page** (scan 5), extracted by the identical
closed-loop rule, registered against these same p17 targets.

### Natural scale — the researcher's specification (measure the original before resizing)

| Icon source | n | median IoU | p75 | p95 | max |
|---|---|---|---|---|---|
| **p17's own icons** | 670 | **389** | 455 | 577 | 684 |
| **foreign icons (scan 5)** | 400 | **391** | 473 | 574 | 696 |

- **30 of 670** real registrations exceed their target's foreign p95. Chance
  alone would give ≈34. That is **at or below chance**.
- **0 of 670** pass the topology gate (icon endpoints/branches equal to the
  target's at the fitted placement).
- The foreign icons are *slightly ahead* on median, p75 and max.

### Permissive scale ladder (2/3, 3/4, 1/1, 4/3, 3/2), kept for comparison

| Icon source | n | median IoU | p75 | p95 | max |
|---|---|---|---|---|---|
| p17's own icons | 670 | 407 | 485 | 625 | 712 |
| foreign icons (scan 5) | 400 | 412 | 488 | 583 | 683 |

68 of 670 over foreign p95 (≈2× chance), 3 pass topology. **Every one of the
top eight results chose 2/3 or 3/4** — the scale-shrinkage bias already
receipted on p47, reappearing. This is why natural scale is the primary run.

### Which target does each icon prefer?

At natural scale the largest target, **T0 — a block of writing, not a figure
— takes 17 of 67 icons**, the single largest share. Preference tracks target
**area**, not shape.

## 5. Visual verification (the part that decides)

Every top-ranked overlay was opened and looked at. Two examples, both at the
top of their run:

- **icon 3 → T3** (the middle-register kneeling figure), natural scale,
  IoU 684, boundary overlap 966/1000, hausdorff 2 — by eye it is a small arc
  of contour **lying along the figure's hem line**. It is not a registration.
- **icon 65 → T3**, ladder scale, IoU 689 — a fragment shrunk to 2/3 sitting
  on the figure's neck cord. Chamfer 1169/1000, topology differs.

The scores are high and the fits are nothing. Per the standing rule, a
correspondence that does not look exact in the picture is reported as not
exact regardless of its score.

## 6. What this measures — MEASURED and METHOD-LIMITED

**MEASURED.** On p17, with icons and targets disjoint by component identity
and scale locked to the original, the page's own icons register onto the
page's own figures **indistinguishably from icons taken from a different
page**, and no registration survives the topology gate.

**METHOD-LIMITED — the named instrument defect.** Local window IoU on a
**sparse line drawing** is dominated by local **ink density**, not by shape.
Any ~30–40 px form scores ≈400/1000 wherever the target's ink density is
comparable, which is why the real and foreign distributions coincide and why
median IoU sits near 400 for every icon on every target. The objective has
almost no shape selectivity at 684×1350. **The machinery cannot yet address
the correspondence question on this page.**

This is a statement about the objective function. It is **not** a finding
about the researcher's hypothesis, and under rule 1 it closes nothing.

## 7. Known gaps in this run

- **Three of the four figures are targets; the top-left figure (scan
  y180–441 x71–245) is not.** Its component did not clear the size floor
  after the loop icons were removed. Stated, not hidden.
- The icon set includes small loops as well as the large ovals (icon 3 is
  26×15) — closure, not size, is the criterion.
- Negative-space registrations were computed (670 of them) and are in
  `registrations.json`; they are not reported separately because the same
  density argument applies to them with more force.

## 8. The next instrument (a scale, not a gate)

What would give this question a usable objective, in order:

1. **A shape-selective score.** Agreement of *edge orientation* inside inked
   windows, not area overlap — so a fragment lying along a stroke cannot
   score like a matched form.
2. **Density normalisation.** Score against the local ink density the window
   already has, so IoU stops being a proxy for "is there ink here".
3. **Higher-resolution capture.** At 684×1350 an icon is ~35 px across; its
   internal structure is under-resolved, which bounds every number above.

None of these authorizes a conclusion, and none can close anything.
