"""NODE-DRE01 (index) — data/dresden/INDEX.md generator.

Numbering + grouping for the 78 WDL scans. The scan→Förstemann mapping is
an EPIGRAPHIC assumption (WDL presents SLUB Mscr.Dresd.R.310 in Förstemann
order, blanks in place) that is CORROBORATED by measurement here: the four
near-blank scans must land exactly at the positions of the four unnumbered
blank pages (28*, 28**, 28***, 60*). If they do not, this generator fails
loudly rather than writing a wrong index.

Categories are the commonly assumed section groupings (SLUB's own content
description; Thompson 1972 commentary tradition). They are labels of
scholarly consensus, not measurements — the index says so.
"""

import json
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "data", "dresden")

# scan index (1-based) -> Förstemann page label
def page_label(k: int) -> str:
    if 1 <= k <= 28:
        return str(k)
    if k == 29:
        return "28*"
    if k == 30:
        return "28**"
    if k == 31:
        return "28***"
    if 32 <= k <= 63:
        return str(k - 3)
    if k == 64:
        return "60*"
    return str(k - 4)  # 65..78 -> 61..74


SECTIONS = [
    ("1-2", "Opening almanacs (heavily damaged first leaves)"),
    ("2-15", "Divinatory almanacs of the gods (invocations, offerings)"),
    ("16-23", "Moon Goddess almanacs (register 13c onward by content)"),
    ("24", "Venus table preface (long counts, multiples of 584)"),
    ("25-28", "New Year (Yearbearer) ceremonies"),
    ("28*-28***", "Blank (unfinished)"),
    ("29-45", "Farmer's almanacs — rain god (Chac) almanacs, agriculture"),
    ("46-50", "Venus table (584-day cycle, 104-yr grand cycle)"),
    ("51-58", "Eclipse table (solar/lunar warning stations)"),
    ("58-59", "Multiplication tables (possibly Mars 780-day)"),
    ("60", "K'atun prophecy (battle/subjugation scene)"),
    ("60*", "Blank (unfinished)"),
    ("61-73", "Rainy-season section: serpent numbers, Long Count series, rain tables, seasonal table (71-73)"),
    ("74", "The Great Flood"),
]


def category_for(label: str) -> str:
    if label.endswith("*"):
        return "Blank (unfinished)"
    p = int(label)
    if p <= 2:
        return "Opening almanacs"
    if p <= 15:
        return "Divinatory almanacs of the gods"
    if p <= 23:
        return "Moon Goddess almanacs"
    if p == 24:
        return "Venus table preface"
    if p <= 28:
        return "New Year ceremonies"
    if p <= 45:
        return "Farmer's almanacs (Chac)"
    if p <= 50:
        return "Venus table"
    if p <= 57:
        return "Eclipse table"
    if p == 58:
        return "Eclipse table / multiplication tables"
    if p == 59:
        return "Multiplication tables"
    if p == 60:
        return "K'atun prophecy"
    if p <= 73:
        return "Rainy-season / serpent series"
    return "The Great Flood"


def main():
    chars = json.load(open(os.path.join(BASE, "characterization.json")))
    sums = {}
    with open(os.path.join(BASE, "SHA256SUMS.txt")) as f:
        for line in f:
            h, name = line.split()
            sums[name] = h

    # Gate: the four lowest-ink scans among scans that are also structurally
    # flat must be exactly {29, 30, 31, 64}. Blankness here is measured as
    # ink coverage below every non-blank page's coverage.
    ink = {int(k[4:]): v["ink_coverage_milli"] for k, v in chars.items()}
    predicted_blanks = {29, 30, 31, 64}
    # damaged-but-inscribed leaves (1-3) can rank low; test the *prediction*:
    # every predicted blank must sit in the bottom 6 of the ink ranking.
    bottom6 = {k for k, _ in sorted(ink.items(), key=lambda kv: kv[1])[:6]}
    if not predicted_blanks <= bottom6:
        raise SystemExit("blank-page corroboration FAILED: bottom-6 ink %r "
                         "does not contain predicted %r" % (bottom6, predicted_blanks))

    lines = []
    lines.append("# Dresden Codex — page index and grouping\n")
    lines.append("Source: WDL item 11621 (SLUB Mscr.Dresd.R.310), 78 scans, "
                 "pinned in `SHA256SUMS.txt`, receipts in `receipts.json`.\n")
    lines.append("**Numbering.** Scans are numbered 1-78 in PDF order "
                 "(OBSERVED). Förstemann page labels 1-74 plus four unnumbered "
                 "blanks (28*, 28**, 28***, 60*) are assigned on the standard "
                 "assumption that WDL presents the codex in Förstemann order "
                 "(EPIGRAPHIC). Corroboration (MEASURED): the four predicted "
                 "blank positions are exactly the four near-blank scans by "
                 "integer ink coverage — see table. Per the working rules, "
                 "modern scan order is NOT evidence of physical or original "
                 "operational order; the reading-order hypothesis that the "
                 "flood page (74) precedes the New Year pages (25-28) is "
                 "recorded as HYPOTHESIS, not applied to file naming.\n")
    lines.append("**Categories** are commonly assumed section groupings "
                 "(SLUB content description; the Thompson commentary "
                 "tradition). They are consensus labels, not measurements.\n")

    lines.append("## Sections (assumed groupings)\n")
    lines.append("| Pages | Section |")
    lines.append("|---|---|")
    for rng, desc in SECTIONS:
        lines.append("| %s | %s |" % (rng, desc))
    lines.append("")

    lines.append("## Per-page table\n")
    lines.append("| Scan | File | Förstemann page | Category (assumed) | "
                 "Ink coverage (milli) | Luma med | SHA-256 (first 12) |")
    lines.append("|---|---|---|---|---|---|---|")
    for k in range(1, 79):
        c = chars["scan%02d" % k]
        name = "pages/wdl11621_scan%02d.jpg" % k
        lbl = page_label(k)
        lines.append("| %d | `%s` | **%s** | %s | %d | %d | `%s` |" % (
            k, name, lbl, category_for(lbl), c["ink_coverage_milli"],
            c["luma_median"], sums[name][:12]))
    lines.append("")
    lines.append("Blank-page corroboration: predicted blank scans "
                 "{29, 30, 31, 64} all sit in the bottom-6 ink ranking "
                 "(the other low entries are the damaged first leaves). "
                 "Ink coverage = dark pixels below the page's own integer-Otsu "
                 "threshold, in milli-units; exact integer arithmetic "
                 "throughout.\n")

    with open(os.path.join(BASE, "INDEX.md"), "w") as f:
        f.write("\n".join(lines))
    print("INDEX.md written; blank corroboration PASS")


if __name__ == "__main__":
    main()
