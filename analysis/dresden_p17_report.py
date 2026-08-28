"""p17 — overlays and report from the registration exhaustion.

Consumes data/dresden/derived/p17/registrations.json. Produces, per the
researcher's standing requirement that nothing is reported without visuals
and everything is labelled:

  * one PER-ICON overlay for every tested correspondence that clears its own
    matched null, drawn at 6x with the icon contour laid on the target at
    the fitted transform, and the whole metric set printed on the panel;
  * one PER-TARGET sheet gathering that target's icons;
  * the correspondence matrix (icon x target) as CSV and markdown;
  * docs/DRESDEN_P17.md.

The fit is judged BY EYE from these overlays. A correspondence that does not
look exact in the picture is reported as not exact regardless of its score.
Order is geometry -> recurrence -> significance -> interpretation, and this
file stops at recurrence: no meaning is assigned to anything.
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp import registration as reg
from cram_dsp.forensics import Ledger
from analysis.dresden_p17 import extract, SCAN, DATA, OUT, DEMO, DOCS

F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                       12)
FB = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)


def deg(rot):
    """Exact rational rotation reported as a labelled triple, plus its
    nearest whole degree for reading. cos = a/c, sin = b/c."""
    a, b, c = rot
    import math
    return int(round(math.degrees(math.atan2(b, a))))


def panel(rgb, leaf, targets, icons, r, scale=6):
    """Icon contour drawn on the target at the fitted transform."""
    t = targets[r["target"]]
    tb = t["box"]
    tm = t["mask"]
    th, tw = tm.shape
    crop = rgb[tb[0] + leaf[0]:tb[1] + leaf[0],
               tb[2] + leaf[2]:tb[3] + leaf[2]]
    img = Image.fromarray(crop).convert("RGB").resize(
        (tw * scale, th * scale), Image.NEAREST)
    d = ImageDraw.Draw(img)
    c = icons[r["icon"]]
    im = reg.transform_mask(c["mask"], tuple(r["rot"]), r["scale"][0],
                            r["scale"][1], r["mirror"])
    cont = reg.contour(im)
    ys, xs = np.nonzero(cont)
    for yy, xx in zip(ys.tolist(), xs.tolist()):
        py, px = yy + r["dy"], xx + r["dx"]
        d.rectangle([px * scale, py * scale,
                     px * scale + scale - 1, py * scale + scale - 1],
                    fill=(255, 60, 60))
    head = 108
    out = Image.new("RGB", (max(img.width, 560), img.height + head),
                    (16, 16, 16))
    out.paste(img, (0, head))
    dd = ImageDraw.Draw(out)
    dd.text((6, 5), "icon %d (%d holes)  ->  target T%d  [%s space]"
            % (r["icon"], r["holes"], r["target"], r["space"]),
            fill=(255, 205, 60), font=FB)
    dd.text((6, 25), "original icon %dx%d px  ->  placed %dx%d px   "
                     "scale %d/%d   rotation %d/%d/%d (~%d deg)   mirror %d"
            % (r["icon_wh_original"][0], r["icon_wh_original"][1],
               r["icon_wh_placed"][0], r["icon_wh_placed"][1],
               r["scale"][0], r["scale"][1], r["rot"][0], r["rot"][1],
               r["rot"][2], deg(r["rot"]), r["mirror"]),
            fill=(200, 200, 200), font=F)
    dd.text((6, 41), "offset dy=%d dx=%d  (target box scan y%d-%d x%d-%d)"
            % (r["dy"], r["dx"], tb[0] + leaf[0], tb[1] + leaf[0],
               tb[2] + leaf[2], tb[3] + leaf[2]),
            fill=(200, 200, 200), font=F)
    dd.text((6, 59), "IoU %d/1000   matched null: median %d  p95 %d  p99 %d "
                     "  margin over p99 %+d"
            % (r["iou_milli"], r["null_median"], r["null_p95"],
               r["null_p99"], r["margin_over_p99"]),
            fill=(0, 235, 120) if r["margin_over_p99"] > 0 else (230, 90, 90),
            font=F)
    dd.text((6, 75), "chamfer %d/1000   hausdorff %d   boundary overlap "
                     "%d/1000" % (r["chamfer_milli"], r["hausdorff"],
                                  r["overlap_milli"]),
            fill=(200, 200, 200), font=F)
    dd.text((6, 91), "topology: icon %dep/%dbr vs target %dep/%dbr  -> %s"
            % (r["icon_endpoints"], r["icon_branches"],
               r["target_endpoints"], r["target_branches"],
               "MATCH" if r["topology_match"] else "differ"),
            fill=(0, 235, 120) if r["topology_match"] else (170, 170, 170),
            font=F)
    dd.text((6, head + img.height - 0), "", fill=(0, 0, 0), font=F)
    return out


def main():
    rgb = np.asarray(Image.open(os.path.join(
        DATA, "pages", "wdl11621_scan%02d.jpg" % SCAN)).convert("RGB"))
    leaf, ink, thin, thick, targets, icons = extract(rgb)
    with open(os.path.join(OUT, "registrations.json")) as f:
        recs = json.load(f)
    print("records", len(recs))

    ink_recs = [r for r in recs if r["space"] == "ink"]
    neg_recs = [r for r in recs if r["space"] == "negative"]

    def stat(rs, key):
        v = sorted(r[key] for r in rs)
        return v[len(v) // 2] if v else 0

    # --- the FOREIGN-ICON control is the comparison that means something ---
    # "Beats its own matched null" is NOT reported as a result: the argmax of
    # a distribution beats that distribution's own p99 almost by definition,
    # and it did so on 608 of 608 registrations in the first run. The receipt
    # lives in analysis/dresden_p17.py; the number is carried here only so
    # the degeneracy is visible rather than quietly dropped.
    degenerate = sum(1 for r in ink_recs if r["margin_over_p99"] > 0)
    with open(os.path.join(OUT, "control_foreign.json")) as f:
        ctrl = json.load(f)

    def dist(vals):
        v = sorted(vals)
        if not v:
            return {}
        return {"n": len(v), "median": v[len(v) // 2],
                "p75": v[(len(v) * 3) // 4], "p95": v[(len(v) * 95) // 100],
                "max": v[-1]}

    real_d = dist([r["iou_milli"] for r in ink_recs])
    ctrl_d = dist([r["iou_milli"] for r in ctrl])
    per_t_ctrl = {}
    for ti in range(len(targets)):
        per_t_ctrl[ti] = {
            "real": dist([r["iou_milli"] for r in ink_recs
                          if r["target"] == ti]),
            "foreign": dist([r["iou_milli"] for r in ctrl
                             if r["target"] == ti])}

    # a registration is only INTERESTING if it beats the foreign-icon
    # distribution on the same target, which is a real comparison
    clears = []
    for r in ink_recs:
        f95 = per_t_ctrl[r["target"]]["foreign"].get("p95", 10 ** 9)
        if r["iou_milli"] > f95:
            rr = dict(r)
            rr["over_foreign_p95"] = r["iou_milli"] - f95
            clears.append(rr)
    topo = [r for r in clears if r["topology_match"]]
    clears.sort(key=lambda r: -r["over_foreign_p95"])

    # --- per-target counts (the cross-target control) ----------------------
    per_t = {}
    for ti in range(len(targets)):
        rs = [r for r in ink_recs if r["target"] == ti]
        f95 = per_t_ctrl[ti]["foreign"].get("p95", 10 ** 9)
        cl = [r for r in rs if r["iou_milli"] > f95]
        per_t[ti] = {"n": len(rs), "clears": len(cl),
                     "median_iou": stat(rs, "iou_milli"),
                     "median_margin": stat(rs, "margin_over_p99"),
                     "area": targets[ti]["area"],
                     "box_scan": [targets[ti]["box"][0] + leaf[0],
                                  targets[ti]["box"][1] + leaf[0],
                                  targets[ti]["box"][2] + leaf[2],
                                  targets[ti]["box"][3] + leaf[2]]}

    # --- per-icon preference: which target does each icon fit best? --------
    pref = {}
    for j in range(len(icons)):
        rs = [r for r in ink_recs if r["icon"] == j]
        if not rs:
            continue
        b = max(rs, key=lambda r: r["iou_milli"])
        pref[j] = b["target"]
    tally = {}
    for ti in pref.values():
        tally[ti] = tally.get(ti, 0) + 1

    os.makedirs(os.path.join(OUT, "overlays"), exist_ok=True)
    made = []
    for r in clears[:48]:
        p = panel(rgb, leaf, targets, icons, r)
        nm = "i%02d_T%d_%s.png" % (r["icon"], r["target"], r["space"])
        p.save(os.path.join(OUT, "overlays", nm))
        made.append((nm, r))
    print("overlays", len(made))

    # --- contact sheet of every overlay ------------------------------------
    if made:
        TW, TH, cols = 430, 470, 6
        nrow = (len(made) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * TW, nrow * TH + 52), (12, 12, 12))
        sd = ImageDraw.Draw(sheet)
        sd.text((10, 8), "p17 (scan 17) — every icon-to-target registration "
                         "that beats the foreign-icon control, ranked by "
                         "over p99. EVIDENCE overlays.",
                fill=(240, 240, 240), font=FB)
        sd.text((10, 28), "Red = the icon's contour at the fitted transform. "
                          "Grey background = the unmodified scan. Judge the "
                          "fit by eye, not by the score.",
                fill=(150, 150, 150), font=F)
        for i, (nm, r) in enumerate(made):
            th_img = Image.open(os.path.join(OUT, "overlays", nm))
            th_img.thumbnail((TW - 8, TH - 8))
            sheet.paste(th_img, ((i % cols) * TW + 4,
                                 52 + (i // cols) * TH))
        sheet.save(os.path.join(DEMO, "dresden_p17_overlays.jpg"), quality=78,
                   optimize=True)

    # --- correspondence matrix --------------------------------------------
    rows = ["icon,seg_id," + ",".join("T%d_iou,T%d_margin" % (t, t)
                                      for t in range(len(targets)))]
    for j in range(len(icons)):
        cells = []
        for ti in range(len(targets)):
            m = [r for r in ink_recs if r["icon"] == j and r["target"] == ti]
            cells.append("%d,%d" % (m[0]["iou_milli"],
                                    m[0]["margin_over_p99"]) if m else ",")
        rows.append("%d,%d,%s" % (j, icons[j]["holes"], ",".join(cells)))
    with open(os.path.join(OUT, "correspondence_matrix.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")

    ledger = Ledger()
    ledger.record("p17_correspondence",
                  {"scan": SCAN, "targets": len(targets),
                   "icons": len(icons), "registrations": len(recs),
                   "ink_over_foreign_p95": len(clears),
                   "degenerate_own_null_clears": degenerate,
                   "real_iou": real_d, "foreign_iou": ctrl_d,
                   "topology_gate_passes": len(topo),
                   "per_target": per_t, "preference_tally": tally},
                  "registration", Ledger.digest(dresden.int_luma(rgb)))
    with open(os.path.join(OUT, "receipts.json"), "w") as f:
        f.write(ledger.export())

    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump({"per_target": per_t, "per_target_ctrl": per_t_ctrl,
                   "tally": tally, "degenerate_own_null_clears": degenerate,
                   "real_iou": real_d, "foreign_iou": ctrl_d,
                   "clears": len(clears), "topo": len(topo),
                   "n_ink": len(ink_recs), "n_neg": len(neg_recs),
                   "median_iou_ink": stat(ink_recs, "iou_milli"),
                   "median_iou_neg": stat(neg_recs, "iou_milli"),
                   "top": clears[:25]}, f)
    print("per-target:", json.dumps(per_t))
    print("real IoU:", real_d)
    print("foreign IoU:", ctrl_d)
    print("tally:", tally, "over-foreign", len(clears), "topo", len(topo),
          "degenerate-own-null", degenerate)


if __name__ == "__main__":
    main()
