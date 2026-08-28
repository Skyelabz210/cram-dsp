# Recurrence of a researcher-selected glyph — p7 element 162, cartouche c2

The researcher pointed at it: *"162 is on this page see it the face"*, and
earlier, *"162 I've seen on other pages."*

**p7 element 162** is a 173×102 block that this repo's detector merged into a
single `figure` — the `stroke_mass` merging defect named in
`docs/DRESDEN_SEGMENTS.md`. Inside it, cartouche **c2** is a face in profile
within a dotted oval frame: eye, snout and jaw all legible **at high
resolution only**. At 684×1350 the glyph is 63×31 px and its interior is not
resolved at all, which is why neither the machine nor the researcher could
read it before `tools/fetch_slub.py`.

Run: `python3 analysis/dresden_recur.py`. Visual:
`demo/dresden_recur_p7_162c2.jpg`. Receipts:
`data/dresden/derived/recur/receipts.json`.

## Method

All 78 pages searched at 1937 px working width, derived from the SLUB
3874×7649 scans — 2.8× the source PDF. Weighted edge-orientation planes,
midrank-normalized on both sides, pooled at 6, compared by exact integer
cosine so scores from different pages share one scale. Eight dihedral poses,
because a recurring sign need not recur upright.

## Control battery

| Control | Result |
|---|---|
| Positive control (self-match, scan 7) | **747/1000, rank 1 of 78** |
| Best other page (hard negative) | scan 19 / p19, **721** |
| Median over all 78 pages | **702** |
| Minimum | 667 |
| **Best near-blank page** | **712** |

Full spread across the codex: **667 → 747, a range of 80**.

## MEASURED — and the method fails its own control

The positive control passes: the query finds its own page first. Everything
above that is not usable.

**Two near-blank pages rank 6th and 7th of 78.** Scan 29 (p28\*) scores 712
and scan 31 (p28\*\*\*) scores 711, above 71 pages that carry writing. The
best genuine other page scores 721 — **just 9 points above blank plaster**,
on a scale whose entire spread is 80.

The contact sheet makes it visible: tiles 6 and 7 of the ranking are bare
plaster with no glyph in them at all.

**METHOD-LIMITED.** A pooled orientation-histogram cosine compares the
*texture statistics* of a sliding window. On a codex where nearly every
window is dense line-work of similar stroke density and orientation mix,
those statistics are near-constant, so the metric has a floor around 700 and
almost no discrimination above it. This is the same **texture floor** already
receipted in `docs/DRESDEN_MACHINE_STATUS.md` for the localizer; it was used
here anyway and it failed the same way.

**No claim is made about whether this glyph recurs.** The measurement cannot
support one in either direction. Under
`docs/RULES_OF_EXPLORATION.md` rule 1 the researcher's recurrence claim
stays **OPEN**, and specifically it is not contradicted by anything here.

## What the search did surface, as candidates only

Two ranked pages hold cartouches that are visibly comparable to the query and
worth the researcher's eye — offered as *candidates to look at*, carrying no
score-based support, since the scores that ranked them also ranked blank
plaster 6th:

- **scan 8 / p8** (709) — an oval cartouche with an internal profile head,
  the closest by eye in the whole sheet.
- **scan 19 / p19** (721) — an oval cartouche with internal curl structure.

## The next instrument (a scale, not a gate)

The question "does *this glyph* recur" should never have been asked of a
sliding-window texture metric. The right comparison is **cartouche to
cartouche**:

1. This repo already segments **11,679 `glyph_block` cells across 78 pages**
   (`data/dresden/segments/`). Each is an individual sign, not a window.
2. Compare the query cartouche against every one of them by *shape* —
   ring/sector signature, dihedral-normalized, plus interior topology
   (holes, endpoints, branch points), all of which this repo has exact
   integer implementations of.
3. Page texture cannot enter such a comparison, because nothing is compared
   except segmented forms. Blank plaster produces no cartouche at all and so
   cannot rank.

That comparison is only now feasible: at 684 px a cartouche interior carries
no measurable structure, and at 3874 px it does.
