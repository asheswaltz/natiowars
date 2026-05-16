"""
trace_borders.py
Auto-trace country borders from europe_south.png white lines,
flood-fill from center points, extract & simplify contours,
then write new level 3 country paths into levels.js.
"""
import os, re, math
import numpy as np
from PIL import Image
from scipy import ndimage

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Canvas / image constants ─────────────────────────────────────────────────
CW, CH = 900, 600
img_path = os.path.join(BASE, 'img', 'europe_south.png')
img = Image.open(img_path).convert('RGB')
W, H = img.size           # 2000 × 1286
scale_s = max(CW/W, CH/H) # 0.46656
x_off   = (CW - W*scale_s) / 2  # -16.56

# canvas ↔ PNG pixel
def canvas_to_px(cx, cy):
    return (cx - x_off) / scale_s, cy / scale_s
def px_to_canvas(px, py):
    return px * scale_s + x_off, py * scale_s

# ─── Detect white border pixels ───────────────────────────────────────────────
arr = np.array(img)        # shape (H, W, 3)
r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]

# "White" borders: high brightness, low saturation
brightness = r.astype(float) + g.astype(float) + b.astype(float)
cmax = np.maximum.reduce([r, g, b]).astype(float)
cmin = np.minimum.reduce([r, g, b]).astype(float)
saturation = np.where(cmax > 0, (cmax - cmin) / cmax, 0)

is_border = (brightness > 600) & (saturation < 0.12)  # near-white pixels
print(f'Border pixels: {is_border.sum()}')

# ─── Create passable mask (non-border, not background) ───────────────────────
# Background is the grey/blue outside Europe — detect as low-saturation but NOT white
# Passable = pixels that are not strong borders
# Dilate border slightly to create walls
border_thick = ndimage.binary_dilation(is_border, iterations=3)
passable = ~border_thick  # can flood-fill through here

# ─── Flood-fill from each country's center ────────────────────────────────────
# Centers in canvas coords → convert to PNG pixel
country_centers_canvas = {
    'royaume_uni': (220, 168),
    'france':      (316, 331),
    'espagne':     (215, 476),
    'pologne':     (604, 197),
}

country_regions = {}
for name, (cx, cy) in country_centers_canvas.items():
    px, py = canvas_to_px(cx, cy)
    seed = (int(round(py)), int(round(px)))
    if not (0 <= seed[0] < H and 0 <= seed[1] < W):
        print(f'{name}: seed OOB')
        continue
    seed_arr = np.zeros((H, W), dtype=bool)
    seed_arr[seed[0], seed[1]] = True
    region = ndimage.binary_fill_holes(
        ndimage.binary_dilation(seed_arr, mask=passable, iterations=10000)
    )
    # Keep only the connected component containing the seed
    labeled, _ = ndimage.label(region)
    region_clean = labeled == labeled[seed[0], seed[1]]
    country_regions[name] = region_clean
    print(f'{name}: region pixels = {region_clean.sum()}')

# ─── Extract contour via marching approach ────────────────────────────────────
def extract_contour(mask, step=8):
    """Raster-scan the boundary and return a polygon in PNG pixel coords."""
    # Find boundary pixels
    eroded = ndimage.binary_erosion(mask)
    boundary = mask & ~eroded
    ys, xs = np.where(boundary)
    if len(xs) == 0:
        return []

    # Order boundary points by angle from centroid
    cy_m = ys.mean()
    cx_m = xs.mean()
    angles = np.arctan2(ys - cy_m, xs - cx_m)
    order = np.argsort(angles)
    pts_ordered = list(zip(xs[order].tolist(), ys[order].tolist()))

    # Subsample every `step` points
    pts = pts_ordered[::step]
    return pts

def douglas_peucker(pts, epsilon):
    """Ramer-Douglas-Peucker polygon simplification."""
    if len(pts) < 3:
        return pts
    def perp_dist(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        if ax == bx and ay == by:
            return math.hypot(px-ax, py-ay)
        d = abs((by-ay)*px - (bx-ax)*py + bx*ay - by*ax) / math.hypot(bx-ax, by-ay)
        return d
    dmax, idx = 0, 0
    for i in range(1, len(pts)-1):
        d = perp_dist(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > epsilon:
        r1 = douglas_peucker(pts[:idx+1], epsilon)
        r2 = douglas_peucker(pts[idx:], epsilon)
        return r1[:-1] + r2
    return [pts[0], pts[-1]]

# ─── Build new paths in canvas coords ────────────────────────────────────────
new_paths = {}
for name, region in country_regions.items():
    contour_px = extract_contour(region, step=6)
    simplified_px = douglas_peucker(contour_px, epsilon=6)
    # Convert to canvas
    canvas_pts = [[round(px_to_canvas(px, py)[0]), round(px_to_canvas(px, py)[1])]
                  for px, py in simplified_px]
    new_paths[name] = canvas_pts
    print(f'{name}: {len(simplified_px)} points after simplification')

# ─── Debug: draw new paths on image ──────────────────────────────────────────
from PIL import ImageDraw
W2, H2 = 900, 600
img_r2 = img.resize((round(W*scale_s), round(H*scale_s)), Image.LANCZOS)
canvas_dbg = Image.new('RGBA', (W2, H2), (30,30,30,255))
canvas_dbg.paste(img_r2, (round(x_off), 0))
draw = ImageDraw.Draw(canvas_dbg, 'RGBA')
colors = {
    'royaume_uni': (0,180,255,170),
    'france':      (50,220,50,170),
    'espagne':     (255,80,80,170),
    'pologne':     (255,200,0,170),
}
for name, pts in new_paths.items():
    if pts:
        draw.polygon([tuple(p) for p in pts], fill=colors[name], outline=(255,255,255,255))
canvas_dbg.save(os.path.join(BASE, 'img', 'debug_level3_new.png'))
print('Saved debug_level3_new.png')

# ─── Patch levels.js ─────────────────────────────────────────────────────────
def fmt_path(pts, indent='        '):
    rows = []
    for i in range(0, len(pts), 5):
        chunk = pts[i:i+5]
        rows.append(indent + ', '.join(f'[{p[0]},{p[1]}]' for p in chunk))
    return ',\n'.join(rows)

levels_path = os.path.join(BASE, 'levels.js')
with open(levels_path, 'r', encoding='utf-8') as f:
    src = f.read()

# Find level 3 block and replace path for each country
for cid, pts in new_paths.items():
    if not pts:
        continue
    # Find the path array for this country within level 3
    # Pattern: id: 'cid', ... path: [ ... ]
    # We need to replace only within level 3 block
    m3_start = src.index('\n  3: {')
    m4_start = src.index('\n  4: {')
    level3 = src[m3_start:m4_start]

    # Find the country block by id
    cid_marker = f"id: '{cid}'"
    cid_pos = level3.index(cid_marker)
    path_start = level3.index('path: [', cid_pos)
    path_end   = level3.index(']', path_start + 7)
    # Include the closing ]
    path_end += 1

    new_path_str = 'path: [\n' + fmt_path(pts) + '\n        ]'
    level3_new = level3[:path_start] + new_path_str + level3[path_end:]
    src = src[:m3_start] + level3_new + src[m4_start:]

    # Also update center
    cx, cy = country_centers_canvas[cid]
    center_old = f'center: {{ x: {cx}, y: {cy} }}'
    # recompute position within updated src
    m3_start = src.index('\n  3: {')
    m4_start = src.index('\n  4: {')
    level3 = src[m3_start:m4_start]
    # center is already correct (we're keeping them)

with open(levels_path, 'w', encoding='utf-8') as f:
    f.write(src)

# Validate
import subprocess
result = subprocess.run(
    ['node','--input-type=module','-e',
     "import {readFileSync} from 'fs'; const src=readFileSync('levels.js','utf8');"
     "const F=Function; new F(src+'; return LEVELS;')();"
     "console.log('OK');"],
    cwd=BASE, capture_output=True, text=True)
print(result.stdout.strip() or result.stderr.strip())
