"""
improve_level3.py — apply improved, manually-traced polygon paths for
level 3 countries, then generate a debug image for verification.
"""
import os, subprocess
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Improved paths (canvas coords 900×600, traced from grid image) ───────────
# All coordinates read with 25px grid as reference, refined to match white border lines

IMPROVED = {
    'royaume_uni': {
        'center': (202, 155), 'dotSize': 28,
        'path': [
            # Great Britain only — clockwise from N Scotland tip
            # NW → N → NE
            [155, 75], [165, 58], [195, 52], [222, 57], [243, 62],
            # NE coast → E coast (Aberdeen → Newcastle → Hull)
            [260, 78], [268, 100], [275, 128], [280, 152], [285, 178],
            # SE England (London → Dover area)
            [289, 200], [292, 220], [284, 240],
            # S coast (Brighton → Cornwall) — pulled up ~8px to show English Channel gap
            [263, 245], [232, 248], [198, 246],
            # SW (Devon) → W Wales → N Wales
            [170, 234], [150, 225], [138, 208],
            # NW England (Lake District) → SW Scotland → NW Scotland
            [138, 185], [140, 158], [145, 135],
            # W Scotland coast
            [150, 110], [148, 85],
        ]
    },
    'france': {
        'center': (316, 345), 'dotSize': 35,
        'path': [
            # Clockwise from N coast (Calais/Belgium border)
            [338, 238], [355, 248], [375, 258], [396, 270],
            # NE Alsace → Swiss border → SE Alps / Mediterranean
            [408, 290], [408, 320], [406, 355], [402, 390],
            # SE Mediterranean coast → Pyrenees E
            [395, 416], [362, 432], [335, 436], [305, 432],
            # Pyrenees W (Spain border) → Atlantic (Biarritz)
            [278, 435], [264, 420],
            # Atlantic: Bay of Biscay going N, then Brittany peninsula jutting W
            [218, 393], [200, 380], [168, 365], [158, 348],
            # Brittany tip → back east → Loire
            [173, 330], [215, 312], [218, 290],
            # Channel coast (pushed down vs UK — gap = English Channel)
            [220, 275], [242, 262], [272, 248], [308, 241],
        ]
    },
    'espagne': {
        'center': (215, 477), 'dotSize': 35,
        'path': [
            # Clockwise from NW (Galicia)
            [148, 400], [168, 404], [185, 407], [200, 410],
            [218, 409], [232, 412], [248, 416], [262, 420],
            # Pyrenees → NE Spain (Mediterranean)
            [278, 433], [306, 432], [335, 436], [362, 432],
            # E coast (Catalonia → Valencia → Murcia)
            [368, 445], [356, 462], [340, 477],
            # SE corner (Almeria → Granada coast)
            [328, 493], [308, 507], [295, 521],
            # S coast (Gibraltar)
            [278, 540], [263, 553], [248, 563],
            # S → SW coast
            [236, 570], [218, 573], [200, 572],
            # W coast (Portugal border → Galicia)
            [184, 578], [168, 568], [162, 553], [155, 540],
            [156, 522], [162, 508], [158, 495],
            # W coast going N
            [162, 480], [165, 460], [172, 450], [168, 435],
            # NW coast back to start
            [155, 427], [147, 418], [140, 407],
        ]
    },
    'pologne': {
        'center': (618, 202), 'dotSize': 35,
        'path': [
            # Clockwise from NW
            [533, 148], [562, 143], [598, 142], [628, 142], [656, 147],
            # N coast (Baltic) → NE
            [680, 156], [700, 168],
            # E border
            [708, 188], [706, 212], [700, 235],
            # SE border (Tatra mountains area)
            [692, 255], [668, 268], [642, 272],
            # S border (Slovak/Czech)
            [612, 268], [582, 268], [557, 260],
            # SW border (Silesia into Germany)
            [538, 248], [530, 230], [528, 208],
            # W border (Oder/Neisse rivers)
            [530, 183], [532, 161],
        ]
    },
}

# ─── Write improved paths into levels.js ─────────────────────────────────────
def fmt_path(pts):
    rows = []
    for i in range(0, len(pts), 5):
        rows.append('        ' + ', '.join(f'[{p[0]},{p[1]}]' for p in pts[i:i+5]))
    return ',\n'.join(rows)

def country_block(id_, name, owner, uP, pop, cx, cy, dot, flag, path):
    return (f"      {{\n        id: '{id_}', name: '{name}', ownerId: {owner},\n"
            f"        unitsPrecise: {uP}, populationTier: {pop},\n"
            f"        center: {{ x: {cx}, y: {cy} }}, dotSize: {dot}, flagCode: '{flag}',\n"
            f"        path: [\n{fmt_path(path)}\n        ]\n      }}")

meta = {
    'royaume_uni': ('Royaume-Uni', 1, 6, 5, 'gb'),
    'france':      ('France',      2, 7, 5, 'fr'),
    'espagne':     ('Espagne',     3, 6, 3, 'es'),
    'pologne':     ('Pologne',     4, 5, 2, 'pl'),
}
order = ['royaume_uni','france','espagne','pologne']

countries_js = ',\n'.join(
    country_block(
        cid, meta[cid][0], meta[cid][1], meta[cid][2], meta[cid][3],
        IMPROVED[cid]['center'][0], IMPROVED[cid]['center'][1],
        IMPROVED[cid]['dotSize'], meta[cid][4], IMPROVED[cid]['path'])
    for cid in order
)

L3 = (
  "  3: {\n"
  "    title: 'Niveau 3 \u2014 Europe du Sud',\n"
  "    svg: 'img/europe_south.png',\n"
  "    ai: {\n"
  "      1: { difficulty: 'facile', thinkInterval: 1, minUnitsToAttack: 10, focusPlayerWeight: 0.6 },\n"
  "      2: { difficulty: 'facile', thinkInterval: 1, minUnitsToAttack: 10, focusPlayerWeight: 0.6 },\n"
  "      3: { difficulty: 'facile', thinkInterval: 1, minUnitsToAttack: 10, focusPlayerWeight: 0.6 },\n"
  "      4: { difficulty: 'facile', thinkInterval: 1, minUnitsToAttack: 10, focusPlayerWeight: 0.6 }\n"
  "    },\n"
  "    grades: { S: 30, A: 60, B: 90, C: 120 },\n"
  "    countries: [\n"
  f"{countries_js}\n"
  "    ]\n"
  "  }"
)

levels_path = os.path.join(BASE, 'levels.js')
with open(levels_path, 'r', encoding='utf-8') as f:
    src = f.read()
m3 = src.index('\n  3: {') + 1
m4 = src.index('\n  4: {') + 1
src = src[:m3] + L3 + ',\n' + src[m4:]
with open(levels_path, 'w', encoding='utf-8') as f:
    f.write(src)

r = subprocess.run(
    ['node','--input-type=module','-e',
     "import {readFileSync} from 'fs'; const src=readFileSync('levels.js','utf8');"
     "const F=Function; new F(src+'; return LEVELS;')(); console.log('OK');"],
    cwd=BASE, capture_output=True, text=True)
print('levels.js:', r.stdout.strip() or r.stderr.strip())

# ─── Debug image ─────────────────────────────────────────────────────────────
CW, CH = 900, 600
img_src = Image.open(os.path.join(BASE, 'img', 'europe_south.png')).convert('RGB')
W, H = img_src.size
ss = max(CW/W, CH/H); xo = (CW - W*ss) / 2
canvas = Image.new('RGBA', (CW, CH), (0,0,0,255))
canvas.paste(img_src.resize((round(W*ss), round(H*ss)), Image.LANCZOS), (round(xo), 0))
draw = ImageDraw.Draw(canvas, 'RGBA')
colors = {'royaume_uni':(0,180,255,255),'france':(50,220,50,255),'espagne':(255,80,80,255),'pologne':(255,200,0,255)}
for cid, d in IMPROVED.items():
    pts = [tuple(p) for p in d['path']]
    draw.polygon(pts, fill=colors[cid][:3]+(55,), outline=colors[cid])
    cx, cy = d['center']
    draw.ellipse((cx-6,cy-6,cx+6,cy+6), fill=(255,255,255,230))
# Grid
for x in range(0, CW, 50):
    draw.line([(x,0),(x,CH)], fill=(255,255,255,35), width=1)
for y in range(0, CH, 50):
    draw.line([(0,y),(CW,y)], fill=(255,255,255,35), width=1)
canvas.save(os.path.join(BASE, 'img', 'debug_level3_improved.png'))
print('Saved debug_level3_improved.png')
