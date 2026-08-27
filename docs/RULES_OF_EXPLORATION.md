# Rules of exploration — Dresden machinery (binding on the agent)

Set by the researcher, 2026-08-27. These rules govern all work on the Dresden
visual-analysis subsystem. They are stated here once and referenced from
CLAUDE.md; violating them is a build failure, not a style issue.

## 1. No hypothesis closure while the machinery is under construction

The current phase is GETTING THE MACHINE RIGHT, not adjudicating the
researcher's hypotheses. Until the researcher declares the machinery
validated for a given question, the agent is NOT AUTHORIZED to mark any
researcher hypothesis as closed, refuted, rejected, killed, or negative —
in any document, commit message, or report. A mis-firing or unvalidated
instrument must never be allowed to close an avenue.

Permitted vocabulary for results: MEASURED (a number, with method and
parameters), METHOD-LIMITED (the current machinery cannot yet address the
question, and why), OPEN (awaiting validated machinery or researcher
interpretation). The machine discovers; the researcher interprets.

There is no "closed avenues" section anywhere in this repo, and none may be
created.

## 2. Controls must not presuppose the hypothesis false

Lesson from the blank-page control: under the researcher's hypothesis the
codex is a continuous physical strip, trails may run THROUGH page
boundaries, and FLAT WHITE IS THE BASE STATE of the effect — so blank pages
carrying trail structure is consistent with the hypothesis, not evidence
against it. A control is only valid if its null model is agreed to be
outside the hypothesis. Every control ships with a statement of what it
assumes; controls whose assumptions the hypothesis rejects are recorded as
measurements, not verdicts.

## 3. Failed methods are receipts, never deletions

When a method is replaced, the record keeps the full provenance chain:
previous method → result → failure mechanism → replacement → confirmation →
verification. The false-negative C4 entry (median-centred luma SAD) is the
template. History is never silently rewritten.

## 4. Evidence representation vs visualization

Two output classes, always labeled:
- EVIDENCE: exact, reversible/traceable transforms of the scan integers.
  All matching, scoring, and measurement runs on these only.
- VISUALIZATION: aggressive contrast, false color, overlays — for human
  eyes. Never fed to a matcher; enhancement must never create information
  ("don't lighten the Sharpie and then pattern-match the artifact").

## 5. Localization control battery

Every localization run reports, alongside the winner: a positive control
(known crop → its own page), a negative control (unrelated crop), a null
control (texture-only template), a hard negative (the most similar other
page), the margins over each, and the winner's rank percentile. "Scan X
wins" alone is not a result.

## 6. Ordering algorithms must not manufacture paths

Any claimed sequence over nodes ships with at least three independently
constructed orderings (brightness ranking; spatial-graph order;
gradient-flow/constrained path) and their exact agreement statistics.
An ordering produced by a single algorithm is a visualization, not a
finding.

## 7. Morphology before semantics

Detectors measure form (size, circularity, fill, spacing, recurrence);
they never bake in interpretations (e.g. "stitching holes"). Hypothesized
semantics are tested as predictions over the measured attributes.
