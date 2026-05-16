"""
restore_level3.py — restore the level 3 country paths to the correct
europe_south.png-transformed coordinates and fix the corrupted path arrays.
Also generates a debug overlay with OUTLINES + GRID so we can visually
verify and refine the paths.
"""
import os, re
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Correct level 3 paths (canvas coords, transformed from europe.png) ──────
# These are the known-good paths from after fix_europe_south.py ran

CORRECT_PATHS = {
    'royaume_uni': {
        'center': (220, 168), 'dotSize': 28,
        'path': [
            [235,63],[235,67],[224,75],[221,83],[223,85],
            [255,85],[248,99],[236,109],[239,112],[232,119],
            [235,121],[243,120],[256,129],[261,148],[272,155],
            [277,163],[279,168],[276,169],[276,172],[281,176],
            [284,181],[281,187],[283,192],[285,193],[291,189],
            [301,191],[305,199],[303,207],[291,216],[289,224],
            [300,227],[295,231],[287,235],[263,233],[252,236],
            [249,239],[236,244],[225,257],[219,259],[199,247],
            [217,225],[199,217],[177,213],[161,223],[139,225],
            [128,211],[140,192],[133,180],[140,159],[164,145],
            [180,137],[183,135],[199,137],[196,121],[199,128],
            [193,127],[199,132],[196,129],[188,129],[193,127],
            [196,132],[192,128],[189,128],[191,127],[203,119],
            [195,125],[196,112],[204,120],[217,131],[215,125],
            [217,120],[213,116],[205,115],[204,117],[209,101],
            [207,100],[201,104],[200,103],[205,92],[203,87],
            [204,81],[211,77],[208,72],[213,69],[213,64],
            [232,64]
        ]
    },
    'france': {
        'center': (316, 331), 'dotSize': 35,
        'path': [
            [318,236],[320,236],[326,243],[331,243],[334,248],
            [344,255],[346,260],[355,262],[366,271],[379,272],
            [386,279],[404,283],[398,302],[398,312],[396,315],
            [394,314],[388,316],[388,322],[380,330],[375,346],
            [375,348],[378,350],[384,343],[387,343],[387,348],
            [390,351],[387,356],[392,367],[387,368],[386,374],
            [390,379],[391,392],[399,398],[402,396],[399,402],
            [387,414],[382,416],[376,416],[363,408],[355,410],
            [348,404],[335,415],[331,420],[331,431],[326,434],
            [318,434],[314,430],[298,423],[295,423],[294,426],
            [283,426],[280,423],[264,418],[262,411],[270,382],
            [270,366],[274,374],[276,374],[275,363],[270,358],
            [270,344],[268,342],[258,336],[255,331],[256,326],
            [254,320],[250,318],[250,315],[234,310],[231,307],
            [220,307],[220,296],[219,294],[216,294],[219,291],
            [227,291],[235,287],[244,294],[250,291],[260,292],
            [266,290],[263,284],[263,276],[259,268],[264,268],
            [267,274],[272,275],[283,276],[288,274],[291,271],
            [291,266],[307,258],[310,252],[310,242],[311,239],
            [316,238]
        ]
    },
    'espagne': {
        'center': (215, 476), 'dotSize': 35,
        'path': [
            [147,407],[155,407],[158,410],[181,408],[199,414],
            [215,411],[223,415],[227,412],[235,416],[243,415],
            [247,418],[250,423],[258,424],[262,428],[266,427],
            [271,431],[282,431],[283,428],[291,430],[295,438],
            [301,436],[303,439],[313,439],[321,436],[321,446],
            [317,450],[307,455],[305,459],[289,464],[281,472],
            [282,475],[279,476],[265,502],[266,515],[273,522],
            [262,530],[257,547],[249,548],[242,555],[237,567],
            [233,564],[227,567],[202,567],[198,571],[189,574],
            [181,584],[174,579],[169,563],[162,556],[154,556],
            [153,550],[162,536],[162,534],[157,530],[157,524],
            [161,520],[162,514],[158,510],[155,502],[159,502],
            [165,494],[165,468],[175,458],[175,454],[170,450],
            [169,444],[159,443],[154,447],[146,446],[143,439],
            [135,442],[138,438],[130,419],[143,414],[146,408]
        ]
    },
    'pologne': {
        'center': (604, 197), 'dotSize': 35,
        'path': [
            [577,145],[588,157],[628,154],[652,158],[648,165],
            [654,162],[683,166],[693,183],[695,197],[686,205],
            [661,217],[658,212],[654,217],[694,211],[693,223],
            [703,246],[682,269],[686,282],[614,262],[620,261],
            [607,258],[621,236],[618,238],[616,233],[614,238],
            [608,237],[601,245],[604,238],[596,238],[593,244],
            [597,252],[601,252],[590,253],[589,233],[576,264],
            [588,266],[570,264],[577,256],[565,257],[561,252],
            [550,253],[553,245],[540,240],[534,220],[532,198],
            [526,184],[530,164],[533,168],[536,162],[542,161],
            [544,173],[548,176],[548,165],[553,166],[550,164],
            [554,157],[556,170],[564,158],[562,152],[569,149],
            [572,154],[576,146]
        ]
    },
}

# ─── Utility: write a path as JS ─────────────────────────────────────────────
def fmt_path_js(pts):
    rows = []
    for i in range(0, len(pts), 5):
        chunk = pts[i:i+5]
        rows.append('        ' + ', '.join(f'[{p[0]},{p[1]}]' for p in chunk))
    return ',\n'.join(rows)

# ─── Fix levels.js with correct bracket-depth path replacement ───────────────
def find_matching_bracket(text, start):
    """Find the position of the closing ] that matches the [ at text[start]."""
    depth = 0
    i = start
    while i < len(text):
        if text[i] == '[':
            depth += 1
        elif text[i] == ']':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError('No matching ]')

levels_path = os.path.join(BASE, 'levels.js')
with open(levels_path, 'r', encoding='utf-8') as f:
    src = f.read()

m3_start = src.index('\n  3: {')
m4_start = src.index('\n  4: {')

level3 = src[m3_start:m4_start]

for cid, data in CORRECT_PATHS.items():
    # Locate country by id
    cid_pos = level3.index(f"id: '{cid}'")
    # Find path: [
    p_kw = level3.index('path: [', cid_pos)
    bracket_open = level3.index('[', p_kw + 5)  # the '[' of the array
    bracket_close = find_matching_bracket(level3, bracket_open)

    new_path_block = '[\n' + fmt_path_js(data['path']) + '\n        ]'
    level3 = level3[:bracket_open] + new_path_block + level3[bracket_close+1:]

    print(f'{cid}: path restored ({len(data["path"])} points)')

src = src[:m3_start] + level3 + src[m4_start:]

with open(levels_path, 'w', encoding='utf-8') as f:
    f.write(src)

# ─── Validate ─────────────────────────────────────────────────────────────────
import subprocess
r = subprocess.run(
    ['node','--input-type=module','-e',
     "import {readFileSync} from 'fs'; const src=readFileSync('levels.js','utf8');"
     "const F=Function; new F(src+'; return LEVELS;')(); console.log('OK');"],
    cwd=BASE, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())

# ─── Generate improved debug: outlines + 50px grid ───────────────────────────
CW, CH = 900, 600
img_src = Image.open(os.path.join(BASE, 'img', 'europe_south.png')).convert('RGB')
W, H = img_src.size
scale_s = max(CW/W, CH/H)
x_off = (CW - W*scale_s) / 2

rw = round(W*scale_s); rh = round(H*scale_s)
img_r = img_src.resize((rw, rh), Image.LANCZOS)
canvas = Image.new('RGBA', (CW, CH), (0,0,0,255))
canvas.paste(img_r, (round(x_off), 0))
draw = ImageDraw.Draw(canvas, 'RGBA')

# Grid every 50px
for x in range(0, CW, 50):
    draw.line([(x,0),(x,CH)], fill=(255,255,255,40), width=1)
    draw.text((x+2, 2), str(x), fill=(255,255,255,180))
for y in range(0, CH, 50):
    draw.line([(0,y),(CW,y)], fill=(255,255,255,40), width=1)
    draw.text((2, y+2), str(y), fill=(255,255,255,180))

# Draw outlines only (not filled) for each country
colors = {
    'royaume_uni': (0,180,255,255),
    'france':      (50,220,50,255),
    'espagne':     (255,80,80,255),
    'pologne':     (255,200,0,255),
}
for cid, data in CORRECT_PATHS.items():
    pts = [tuple(p) for p in data['path']]
    # Draw outline polygon
    draw.polygon(pts, fill=colors[cid][:3] + (50,), outline=colors[cid])
    # Mark center
    cx, cy = data['center']
    r = 6
    draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(255,255,255,230))
    draw.text((cx+8, cy-8), cid[:3], fill=(255,255,255,220))

canvas.save(os.path.join(BASE, 'img', 'debug_level3_grid.png'))
print('Saved debug_level3_grid.png')
