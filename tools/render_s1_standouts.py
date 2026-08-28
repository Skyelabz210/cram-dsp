"""Render the S1 standout pages — the panels behind docs/DRESDEN_SCALES.md.

Reads the standout list straight out of the generated report (never a
hand-transcribed list: an earlier hand copy put the wrong two pages in the
panel, caught on review and receipted here), then draws all three orderings
on each page — brightness (yellow), spatial (cyan), gradient-flow (magenta) —
with the brightness ranks circled.

These are VISUALIZATION outputs per docs/RULES_OF_EXPLORATION.md rule 4: no
matcher ever reads them.

Usage: python3 tools/render_s1_standouts.py
"""

import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from cram_dsp import dresden

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DATA = os.path.join(_ROOT, 'data', 'dresden')
DEMO = os.path.join(_ROOT, 'demo')
LIMIT=12
# (scan, page_label, observed, shuffled_max)
import re
_rep = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                         'docs', 'DRESDEN_SCALES.md')).read()
_m = re.search(r"exceeded every shuffle: (.+?)\.\n", _rep, re.S)
STAND = [(0, l, int(o), int(mx)) for l, o, mx in
         re.findall(r"p([0-9]+\*{0,3}) \(obs (\d+) vs shuffled max (\d+)\)",
                    _m.group(1))]
# resolve scan numbers from page labels used in the report
def scan_of(lbl):
    if lbl.endswith('*'):
        base=int(lbl.rstrip('*')); stars=len(lbl)-len(str(base))
        return 28+stars if base==28 else 64
    p=int(lbl); return p if p<=28 else (p+3 if p<=60 else p+4)
STAND=[(scan_of(l),l,o,m) for _,l,o,m in STAND]

COL={'A':(255,200,30),'B':(0,220,255),'C':(255,90,200)}
W,H=228,450
grid=Image.new('RGB',(W*4+30, (H+40)*2+16),(12,12,12))
gd=ImageDraw.Draw(grid)
gd.text((8,4),"S1 standouts — pages whose 3-ordering agreement beat EVERY position shuffle",fill=(232,223,206))
gd.text((8,18),"A brightness   B spatial   C gradient-flow",fill=(160,150,130))
for i,(k,lbl,obs,shmax) in enumerate(STAND):
    rgb=np.asarray(Image.open(f'{DATA}/pages/wdl11621_scan{k:02d}.jpg').convert('RGB'))
    thr,recs=dresden.node_records(rgb)
    A=dresden.order_brightness(recs,LIMIT); B=dresden.order_spatial(recs,LIMIT); C=dresden.order_gradient_flow(recs,LIMIT)
    im=Image.fromarray(rgb).convert('RGB')
    d=ImageDraw.Draw(im)
    for seq,key in ((A,'A'),(B,'B'),(C,'C')):
        pts=[(recs[j][1],recs[j][0]) for j in seq]
        for a,b in zip(pts,pts[1:]): d.line([a,b],fill=COL[key],width=3)
    for r,j in enumerate(A[:6]):
        cy,cx=recs[j][0],recs[j][1]
        d.ellipse([cx-10,cy-10,cx+10,cy+10],outline=(255,255,255),width=3)
        d.text((cx+12,cy-8),str(r+1),fill=(255,255,255))
    im=im.resize((W,H),Image.LANCZOS)
    x=6+(i%4)*(W+6); y=34+(i//4)*(H+40)
    grid.paste(im,(x,y))
    gd.text((x,y+H+3),"p%s  obs %d  vs shuffled max %d  (+%d)"%(lbl,obs,shmax,obs-shmax),fill=(120,230,150))
    gd.text((x,y+H+17),"%d white nodes"%len(recs),fill=(150,140,120))
grid.save(f'{DEMO}/dresden_s1_standouts.png')
print("saved grid", grid.size)

# the two largest gaps, big
for k,lbl,obs,shmax in [s for s in STAND if s[1] in ('74','59')]:
    rgb=np.asarray(Image.open(f'{DATA}/pages/wdl11621_scan{k:02d}.jpg').convert('RGB'))
    thr,recs=dresden.node_records(rgb)
    A=dresden.order_brightness(recs,LIMIT); B=dresden.order_spatial(recs,LIMIT); C=dresden.order_gradient_flow(recs,LIMIT)
    S=2
    im=Image.fromarray(rgb).convert('RGB').resize((684*S,1350*S),Image.LANCZOS)
    d=ImageDraw.Draw(im)
    for seq,key in ((A,'A'),(B,'B'),(C,'C')):
        pts=[(recs[j][1]*S,recs[j][0]*S) for j in seq]
        for a,b in zip(pts,pts[1:]): d.line([a,b],fill=COL[key],width=4)
    for r,j in enumerate(A[:LIMIT]):
        cy,cx=recs[j][0]*S,recs[j][1]*S
        d.ellipse([cx-16,cy-16,cx+16,cy+16],outline=(255,255,255),width=4)
        d.text((cx+19,cy-10),str(r+1),fill=(255,255,255))
    hdr=Image.new('RGB',(im.width,im.height+34),(12,12,12)); hdr.paste(im,(0,34))
    hd=ImageDraw.Draw(hdr)
    hd.text((8,6),"p%s — agreement %d, above every shuffle (max %d). A brightness / B spatial / C gradient-flow; 1-12 = brightness rank"%(lbl,obs,shmax),fill=(120,230,150))
    hdr.resize((im.width//2, (im.height+34)//2), Image.LANCZOS).save(f'{DEMO}/dresden_s1_p{lbl}.png')
    print("saved p"+lbl)
