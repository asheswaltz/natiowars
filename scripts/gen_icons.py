"""
Génère icon-192.png et icon-512.png depuis app-icon.svg
en utilisant Pillow (pas de dépendance cairo).
"""
from PIL import Image, ImageDraw
import math, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'img')

def make_icon(size):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 512  # facteur d'échelle

    def sc(v): return v * s           # scalaire
    def sp(x, y): return (x*s, y*s)  # point

    # Fond arrondi dégradé (simulé par deux rectangles + coins)
    radius = int(110 * s)
    # Dégradé fond #10263b -> #163f63 (vertical)
    for y in range(size):
        t = y / size
        r = int(0x10 + (0x16 - 0x10) * t)
        g = int(0x26 + (0x3f - 0x26) * t)
        b = int(0x3b + (0x63 - 0x3b) * t)
        d.rectangle([0, y, size, y+1], fill=(r, g, b, 255))

    # Masque coins arrondis
    mask = Image.new('L', (size, size), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle([0, 0, size-1, size-1], radius=radius, fill=255)
    img.putalpha(mask)
    d = ImageDraw.Draw(img)

    # Globe dégradé #58d68d -> #2e86de
    cx, cy, r = size//2, size//2, int(164*s)
    for y in range(cy - r, cy + r + 1):
        y = int(y)
        if y < 0 or y >= size: continue
        dy = y - cy
        if abs(dy) > r: continue
        dx = math.sqrt(r*r - dy*dy)
        x0, x1 = int(cx - dx), int(cx + dx)
        t = (y - (cy - r)) / (2 * r)
        gr = int(0x58 + (0x2e - 0x58) * t)
        gg = int(0xd6 + (0x86 - 0xd6) * t)
        gb = int(0x8d + (0xde - 0x8d) * t)
        d.line([(x0, y), (x1, y)], fill=(gr, gg, gb, 255))

    # Méridiens / parallèles (blanc semi-transparent)
    lw = max(1, int(12*s))
    wc = (255, 255, 255, 97)
    # Grande ellipse verticale
    d.ellipse([sc(256-122), sc(256-164), sc(256+122), sc(256+164)],
              outline=wc, width=lw)
    # Petite ellipse
    d.ellipse([sc(256-60), sc(256-164), sc(256+60), sc(256+164)],
              outline=(255,255,255,89), width=max(1,int(11*s)))
    # Parallèles horizontaux
    for py in [188, 256, 324]:
        d.line([sp(108 if py==256 else 136, py),
                sp(404 if py==256 else 376, py)],
               fill=wc, width=lw)

    # Contour jaune (polygone Nation Wars)
    pts = [(152,120),(360,176),(312,232),(368,280),(296,384),(160,360),(208,288),(136,240)]
    scaled = [sp(x, y) for x, y in pts]
    d.line(scaled + [scaled[0]], fill=(241,196,15,255), width=max(2,int(22*s)))

    return img

for sz in [192, 512]:
    icon = make_icon(sz)
    path = os.path.join(OUT, f'icon-{sz}.png')
    icon.save(path, 'PNG')
    print(f'Saved {path}')
