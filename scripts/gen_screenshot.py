"""
Génère img/screenshot1.png (1280x720) – maquette de l'écran Nation Wars
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = os.path.join(os.path.dirname(__file__), '..', 'img', 'screenshot1.png')
W, H = 1280, 720

img = Image.new('RGB', (W, H), (13, 27, 42))
d = ImageDraw.Draw(img)

# ── Fond dégradé ──────────────────────────────────────────────────────────────
for y in range(H):
    t = y / H
    r = int(13 + (22 - 13) * t)
    g = int(27 + (45 - 27) * t)
    b = int(42 + (74 - 42) * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# ── Continents simplifiés (silhouettes) ───────────────────────────────────────
continent_color = (25, 60, 90, 180)
# Europe / Asie
d.ellipse([550, 60, 980, 420], fill=(22, 55, 85))
# Amériques
d.ellipse([40, 80, 380, 500], fill=(20, 52, 80))
# Afrique
d.ellipse([540, 280, 780, 600], fill=(22, 55, 85))
# Océanie
d.ellipse([920, 380, 1180, 580], fill=(20, 52, 80))

# Lignes de grille (méridiens / parallèles)
grid_col = (255, 255, 255, 20)
for x in range(0, W, 120):
    d.line([(x, 0), (x, H)], fill=(30, 70, 100))
for y in range(0, H, 120):
    d.line([(0, y), (W, y)], fill=(30, 70, 100))

# ── Logo "NATION WARS" ────────────────────────────────────────────────────────
# Lettres colorées simulées par blocs
logo_text = "NATION WARS"
logo_x, logo_y = 340, 30
colors = [(241,196,15),(88,214,141),(46,134,222),(231,76,60),(155,89,182),
          (52,152,219),(241,196,15),(88,214,141),(46,134,222),(231,76,60),(155,89,182)]
try:
    font_big = ImageFont.truetype("arial.ttf", 90)
    font_med = ImageFont.truetype("arial.ttf", 22)
    font_lv  = ImageFont.truetype("arial.ttf", 32)
    font_lk  = ImageFont.truetype("arial.ttf", 18)
except:
    font_big = ImageFont.load_default()
    font_med = font_big
    font_lv  = font_big
    font_lk  = font_big

# Logo ombre
d.text((logo_x+4, logo_y+4), logo_text, font=font_big, fill=(0, 0, 0, 180))
# Logo principal
d.text((logo_x, logo_y), logo_text, font=font_big, fill=(241, 196, 15))

# Tagline
tagline = "Conquer the world, country by country!"
d.text((20, 150), tagline, font=font_med, fill=(200, 220, 240))

# ── Grille de niveaux ─────────────────────────────────────────────────────────
cols, rows = 5, 4
btn_w, btn_h = 200, 110
gap_x, gap_y = 18, 14
grid_x0 = (W - cols * btn_w - (cols - 1) * gap_x) // 2
grid_y0 = 195

for i in range(20):
    col = i % cols
    row = i // cols
    x0 = grid_x0 + col * (btn_w + gap_x)
    y0 = grid_y0 + row * (btn_h + gap_y)
    x1 = x0 + btn_w
    y1 = y0 + btn_h
    level = i + 1

    if level == 1:
        # Niveau débloqué
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(46, 86, 140))
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, outline=(88, 180, 255), width=2)
        d.text((x0 + btn_w//2 - 15, y0 + btn_h//2 - 22), str(level), font=font_lv, fill=(255, 255, 255))
    else:
        # Niveau verrouillé
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(18, 35, 58))
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, outline=(40, 70, 100), width=1)
        d.text((x0 + btn_w//2 - 18, y0 + 14), str(level), font=font_lv, fill=(80, 110, 150))
        # Cadenas
        lx, ly = x0 + btn_w//2 - 8, y0 + btn_h - 30
        d.rectangle([lx, ly, lx+16, ly+14], outline=(180, 150, 60), width=2)
        d.arc([lx+2, ly-10, lx+14, ly+2], 180, 0, fill=(180, 150, 60), width=2)

img.save(OUT, 'PNG')
print(f'Saved {OUT}')
