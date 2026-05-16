"""
fix_europe_south.py

Recalculates all country path coordinates for levels 3, 4, 5, 6 so they
match europe_south.png instead of europe.png.

Also changes levels 3/4/5 svg from 'img/europe.png' to 'img/europe_south.png'.
Removes Islande, Suède, Finlande from level 5 (not visible on south map).
Regenerates level 6 from the original europe.png coordinates (levels 4/5 source).

Transform derivation
--------------------
europe.png (We × He):
  cover on 900×600 → scale_e = max(900/We, 600/He)
  rendered: We*scale_e × He*scale_e (centered)
  x_offset_e = (900 - We*scale_e) / 2
  y_offset_e = (600 - He*scale_e) / 2

  canvas (cx, cy) → png pixel (px, py):
    px = (cx - x_offset_e) / scale_e
    py = (cy - y_offset_e) / scale_e

europe_south.png was cropped from europe.png at (cx1, cy1, cx2, cy2) then
resized to (Ws × Hs):
  scale_crop_x = Ws / (cx2 - cx1)
  scale_crop_y = Hs / (cy2 - cy1)

  png pixel (px, py) → south pixel (sx, sy):
    sx = (px - cx1) * scale_crop_x
    sy = (py - cy1) * scale_crop_y

europe_south.png (Ws × Hs):
  cover on 900×600 → scale_s = max(900/Ws, 600/Hs)
  x_offset_s = (900 - Ws*scale_s) / 2
  y_offset_s = (600 - Hs*scale_s) / 2

  south pixel (sx, sy) → new canvas (new_cx, new_cy):
    new_cx = sx * scale_s + x_offset_s
    new_cy = sy * scale_s + y_offset_s
"""

import os, re, math
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Load images and compute transform ─────────────────────────────────────
CW, CH = 900, 600

europe     = Image.open(os.path.join(BASE, 'img', 'europe.png'))
europe_s   = Image.open(os.path.join(BASE, 'img', 'europe_south.png'))

We, He = europe.size   # 2000 × 1093
Ws, Hs = europe_s.size  # 2000 × 1286 (approx)

print(f'europe.png     : {We}×{He}')
print(f'europe_south.png: {Ws}×{Hs}')

# europe.png cover scale
scale_e = max(CW/We, CH/He)
x_offset_e = (CW - We*scale_e) / 2
y_offset_e = (CH - He*scale_e) / 2
print(f'europe cover scale: {scale_e:.6f}, x_off: {x_offset_e:.3f}, y_off: {y_offset_e:.3f}')

# europe_south.png crop from europe.png (from make_pngs.py)
CROP = (180, 273, 1455, 1093)
crop_w = CROP[2] - CROP[0]  # 1275
crop_h = CROP[3] - CROP[1]  # 820
scale_crop_x = Ws / crop_w
scale_crop_y = Hs / crop_h
print(f'europe_south crop: {crop_w}×{crop_h}, resize scale: {scale_crop_x:.6f} / {scale_crop_y:.6f}')

# europe_south.png cover scale
scale_s = max(CW/Ws, CH/Hs)
x_offset_s = (CW - Ws*scale_s) / 2
y_offset_s = (CH - Hs*scale_s) / 2
print(f'europe_south cover scale: {scale_s:.6f}, x_off: {x_offset_s:.3f}, y_off: {y_offset_s:.3f}')

def tf(cx, cy):
    """Transform canvas coords (europe.png) → canvas coords (europe_south.png)"""
    # Step 1: canvas → europe.png pixel
    px = (cx - x_offset_e) / scale_e
    py = (cy - y_offset_e) / scale_e
    # Step 2: pixel → south pixel
    sx = (px - CROP[0]) * scale_crop_x
    sy = (py - CROP[1]) * scale_crop_y
    # Step 3: south pixel → canvas
    new_cx = sx * scale_s + x_offset_s
    new_cy = sy * scale_s + y_offset_s
    return round(new_cx), round(new_cy)

def tf_dot(d):
    """Scale a dot size by the zoom factor"""
    zoom = scale_crop_x * scale_s / scale_e
    return round(d * zoom)

# Verify with France center (original: 285, 388)
tc = tf(285, 388)
print(f'\nFrance center test: (285,388) → {tc}')

# ─── Country source data (europe.png canvas coords) ─────────────────────────
# Each entry: (id, name, ownerId_placeholder, unitsPrecise, populationTier, dotSize, flagCode, center, path)
# ownerId will be overridden per-level

COUNTRIES = {
    # ── From Level 3 ──────────────────────────────────────────────────────────
    'royaume_uni_lv3': {
        'id': 'royaume_uni', 'name': 'Royaume-Uni',
        'unitsPrecise': 6, 'populationTier': 5, 'dotSize': 21, 'flagCode': 'gb',
        'center': [214, 279],
        'path': [
            [225,200],[225,203],[217,209],[215,215],[216,217],[240,217],[235,227],[226,235],
            [228,237],[223,242],[225,244],[231,243],[241,250],[245,264],[253,269],[257,275],
            [258,279],[256,280],[256,282],[260,285],[262,289],[260,293],[261,297],[263,298],
            [267,295],[275,296],[278,302],[276,308],[267,315],[266,321],[274,323],[270,326],
            [264,329],[246,328],[238,330],[236,332],[226,336],[218,346],[213,347],[198,338],
            [212,322],[198,316],[182,313],[170,320],[153,322],[145,311],[154,297],[149,288],
            [154,272],[172,262],[184,256],[186,254],[198,256],[196,244],[198,249],[194,248],
            [198,252],[196,250],[190,250],[194,248],[196,252],[193,249],[191,249],[192,248],
            [201,242],[195,247],[196,237],[202,243],[212,251],[210,247],[212,243],[209,240],
            [203,239],[202,241],[206,229],[204,228],[200,231],[199,230],[203,222],[201,218],
            [202,214],[207,211],[205,207],[209,205],[209,201],[223,201]
        ]
    },
    'france_lv3': {
        'id': 'france', 'name': 'France',
        'unitsPrecise': 7, 'populationTier': 5, 'dotSize': 26, 'flagCode': 'fr',
        'center': [284, 399],
        'path': [
            [285,328],[287,328],[291,333],[295,333],[297,337],[305,342],[306,346],[313,347],
            [321,354],[331,355],[336,360],[350,363],[345,377],[345,385],[344,387],[342,386],
            [338,388],[338,392],[332,398],[328,410],[328,412],[330,413],[335,408],[337,408],
            [337,412],[339,414],[337,418],[341,426],[337,427],[336,431],[339,435],[340,445],
            [346,449],[348,448],[346,452],[337,461],[333,463],[329,463],[319,457],[313,458],
            [308,454],[298,462],[295,466],[295,474],[291,476],[285,476],[282,473],[270,468],
            [268,468],[267,470],[259,470],[257,468],[245,464],[243,459],[249,437],[249,425],
            [252,431],[254,431],[253,423],[249,419],[249,409],[248,407],[240,403],[238,399],
            [239,395],[237,391],[234,389],[234,387],[222,383],[220,381],[212,381],[212,373],
            [211,371],[209,371],[211,369],[217,369],[223,366],[230,371],[234,369],[242,370],
            [246,368],[244,364],[244,358],[241,352],[245,352],[247,356],[251,357],[259,358],
            [263,356],[265,354],[265,350],[277,344],[279,340],[279,332],[280,330],[284,329]
        ]
    },
    'espagne_lv3': {
        'id': 'espagne', 'name': 'Espagne',
        'unitsPrecise': 6, 'populationTier': 3, 'dotSize': 26, 'flagCode': 'es',
        'center': [218, 508],
        'path': [
            [167,456],[173,456],[175,458],[192,457],[206,461],[218,459],[224,462],[227,460],
            [233,463],[239,462],[242,464],[244,468],[250,469],[253,472],[256,471],[260,474],
            [268,474],[269,472],[275,473],[278,479],[282,478],[284,480],[291,480],[297,478],
            [297,485],[294,488],[287,492],[285,495],[273,499],[267,505],[268,507],[266,508],
            [255,527],[256,537],[261,542],[253,548],[249,561],[243,562],[238,567],[234,576],
            [231,574],[227,576],[208,576],[205,579],[198,581],[192,589],[187,585],[183,573],
            [178,568],[172,568],[171,563],[178,553],[178,551],[174,548],[174,544],[177,541],
            [178,536],[175,533],[173,527],[176,527],[180,521],[180,502],[188,494],[188,491],
            [184,488],[183,484],[176,483],[172,486],[166,485],[164,480],[158,482],[160,479],
            [154,465],[164,461],[166,457]
        ]
    },
    'pologne_lv3': {
        'id': 'pologne', 'name': 'Pologne',
        'unitsPrecise': 5, 'populationTier': 2, 'dotSize': 26, 'flagCode': 'pl',
        'center': [477, 300],
        'path': [
            [457,261],[465,270],[495,268],[513,271],[510,276],[515,274],[522,296],[519,296],
            [515,304],[521,311],[520,315],[518,311],[515,315],[517,322],[521,322],[527,328],
            [520,327],[493,351],[485,349],[489,348],[492,337],[490,329],[488,331],[486,327],
            [485,331],[480,330],[475,336],[477,331],[471,331],[469,335],[472,341],[475,341],
            [467,342],[466,327],[456,350],[465,352],[452,350],[457,344],[448,345],[445,341],
            [437,342],[439,336],[429,332],[425,317],[423,301],[419,290],[422,275],[424,278],
            [426,274],[431,273],[432,282],[435,284],[435,276],[439,277],[437,275],[440,270],
            [441,280],[447,271],[446,266],[451,264],[453,268],[456,262]
        ]
    },
    # ── From Level 4 ──────────────────────────────────────────────────────────
    'france_lv4': {
        'id': 'france', 'name': 'France',
        'unitsPrecise': 7, 'populationTier': 5, 'dotSize': 26, 'flagCode': 'fr',
        'center': [285, 388],
        'path': [
            [226,385],[214,382],[211,377],[212,365],[224,365],[237,366],[244,358],[243,350],
            [255,354],[265,353],[276,345],[279,330],[287,325],[303,336],[310,346],[322,354],
            [343,360],[349,376],[339,396],[334,408],[339,416],[339,428],[349,451],[334,463],
            [306,453],[296,469],[292,476],[267,469],[252,468],[242,459],[250,420],[249,409]
        ]
    },
    'espagne_lv4': {
        'id': 'espagne', 'name': 'Espagne',
        'unitsPrecise': 6, 'populationTier': 3, 'dotSize': 21, 'flagCode': 'es',
        'center': [228, 517],
        'path': [
            [168,456],[177,459],[192,457],[205,461],[218,459],[224,462],[239,462],[243,468],
            [259,474],[272,472],[278,479],[297,478],[297,485],[294,488],[285,495],[272,499],
            [267,505],[255,527],[256,537],[260,542],[253,548],[249,561],[240,564],[234,576],
            [207,576],[191,588],[187,585],[184,574],[178,568],[172,568],[172,561],[178,554],
            [174,548],[178,536],[173,527],[179,524],[180,502],[188,494],[188,490],[181,483],
            [166,485],[164,480],[158,482],[160,479],[154,465],[167,457]
        ]
    },
    'allemagne_lv4': {
        'id': 'allemagne', 'name': 'Allemagne',
        'unitsPrecise': 8, 'populationTier': 4, 'dotSize': 26, 'flagCode': 'de',
        'center': [371, 324],
        'path': [
            [357,263],[366,264],[368,270],[378,272],[376,275],[384,279],[400,270],[415,283],
            [414,296],[419,301],[425,326],[420,324],[418,328],[394,339],[400,353],[415,366],
            [404,376],[406,383],[399,382],[389,387],[379,385],[377,388],[364,381],[348,384],
            [354,362],[345,357],[337,357],[334,352],[335,347],[331,344],[333,336],[329,331],
            [329,314],[335,314],[339,307],[339,284],[347,283],[351,287],[355,280],[362,279],
            [357,264]
        ]
    },
    'royaume_uni_lv4': {
        'id': 'royaume_uni', 'name': 'Royaume-Uni',
        'unitsPrecise': 7, 'populationTier': 5, 'dotSize': 21, 'flagCode': 'gb',
        'center': [215, 241],
        'path': [
            [191,306],[216,210],[215,216],[239,218],[223,242],[233,244],[241,250],[245,264],
            [257,275],[256,282],[262,288],[260,296],[275,296],[278,302],[276,308],[267,314],
            [266,321],[274,323],[270,326],[264,329],[246,328],[235,332],[227,330],[218,338],
            [212,336],[204,340],[211,329],[217,325],[227,325],[233,317],[230,315],[222,318],
            [204,317],[217,303],[217,295],[214,293],[227,290],[231,274],[223,267],[226,259],
            [207,260],[212,250],[212,242],[203,238],[205,228],[199,231],[203,223],[202,213],
            [206,212],[209,202],[230,197],[178,253],[171,263],[173,269],[162,273],[154,273],
            [156,293],[149,316],[162,318],[176,318]
        ]
    },
    'pologne_lv4': {
        'id': 'pologne', 'name': 'Pologne',
        'unitsPrecise': 5, 'populationTier': 2, 'dotSize': 23, 'flagCode': 'pl',
        'center': [475, 314],
        'path': [
            [452,264],[459,264],[465,272],[497,271],[510,272],[514,275],[522,297],[516,301],
            [515,306],[520,310],[519,316],[528,334],[514,350],[515,358],[504,352],[489,353],
            [485,356],[479,349],[475,353],[468,344],[461,343],[459,337],[449,335],[447,340],
            [444,332],[429,325],[424,314],[423,300],[418,295],[418,283],[422,277],[451,265]
        ]
    },
    # ── From Level 5 ──────────────────────────────────────────────────────────
    'france_lv5': {
        'id': 'france', 'name': 'France',
        'unitsPrecise': 7, 'populationTier': 5, 'dotSize': 26, 'flagCode': 'fr',
        'center': [285, 388],
        'path': [
            [226,385],[214,382],[211,377],[212,365],[224,365],[237,366],[244,358],[243,350],
            [255,354],[265,353],[276,345],[279,330],[287,325],[303,336],[310,346],[322,354],
            [343,360],[349,376],[339,396],[334,408],[339,416],[339,428],[349,451],[334,463],
            [306,453],[296,469],[292,476],[267,469],[252,468],[242,459],[250,420],[249,409]
        ]
    },
    'italie_lv5': {
        'id': 'italie', 'name': 'Italie',
        'unitsPrecise': 6, 'populationTier': 4, 'dotSize': 20, 'flagCode': 'it',
        'center': [435, 493],
        'path': [
            [373,443],[359,440],[351,451],[340,430],[346,416],[359,405],[367,412],[378,405],
            [388,402],[399,400],[418,405],[415,421],[403,431],[407,447],[422,460],[432,478],
            [445,485],[455,497],[474,509],[482,520],[466,513],[457,521],[461,525],[465,537],
            [461,543],[456,553],[444,559],[445,572],[439,578],[421,568],[411,561],[416,550],
            [432,551],[445,549],[453,540],[453,533],[437,512],[429,501],[413,495],[404,488],
            [387,471],[381,453]
        ]
    },
    'espagne_lv5': {
        'id': 'espagne', 'name': 'Espagne',
        'unitsPrecise': 6, 'populationTier': 3, 'dotSize': 23, 'flagCode': 'es',
        'center': [232, 520],
        'path': [
            [168,456],[177,459],[192,457],[205,461],[218,459],[224,462],[239,462],[243,468],
            [259,474],[272,472],[278,479],[297,478],[297,485],[294,488],[285,495],[272,499],
            [267,505],[255,527],[256,537],[260,542],[253,548],[249,561],[240,564],[234,576],
            [207,576],[191,588],[187,585],[184,574],[178,568],[172,568],[172,561],[178,554],
            [174,548],[178,536],[173,527],[179,524],[180,502],[188,494],[188,490],[181,483],
            [166,485],[164,480],[158,482],[160,479],[154,465],[167,457]
        ]
    },
    'allemagne_lv5': {
        'id': 'allemagne', 'name': 'Allemagne',
        'unitsPrecise': 8, 'populationTier': 4, 'dotSize': 26, 'flagCode': 'de',
        'center': [371, 311],
        'path': [
            [357,263],[366,264],[368,270],[378,272],[376,275],[384,279],[400,270],[415,283],
            [414,296],[419,301],[425,326],[420,324],[418,328],[394,339],[400,353],[415,366],
            [404,376],[406,383],[399,382],[389,387],[379,385],[377,388],[364,381],[348,384],
            [354,362],[345,357],[337,357],[334,352],[335,347],[331,344],[333,336],[329,331],
            [329,314],[335,314],[339,307],[339,284],[347,283],[351,287],[355,280],[362,279],
            [357,264]
        ]
    },
    'royaume_uni_lv5': {
        'id': 'royaume_uni', 'name': 'Royaume-Uni',
        'unitsPrecise': 7, 'populationTier': 5, 'dotSize': 23, 'flagCode': 'gb',
        'center': [231, 279],
        'path': [
            [191,306],[216,210],[215,216],[239,218],[223,242],[233,244],[241,250],[245,264],
            [257,275],[256,282],[262,288],[260,296],[275,296],[278,302],[276,308],[267,314],
            [266,321],[274,323],[270,326],[264,329],[246,328],[235,332],[227,330],[218,338],
            [212,336],[204,340],[211,329],[217,325],[227,325],[233,317],[230,315],[222,318],
            [204,317],[217,303],[217,295],[214,293],[227,290],[231,274],[223,267],[226,259],
            [207,260],[212,250],[212,242],[203,238],[205,228],[199,231],[203,223],[202,213],
            [206,212],[209,202],[230,197],[178,253],[171,263],[173,269],[162,273],[154,273],
            [156,293],[149,316],[162,318],[176,318]
        ]
    },
    'pologne_lv5': {
        'id': 'pologne', 'name': 'Pologne',
        'unitsPrecise': 5, 'populationTier': 3, 'dotSize': 20, 'flagCode': 'pl',
        'center': [481, 301],
        'path': [
            [452,264],[459,264],[465,272],[497,271],[510,272],[514,275],[522,297],[516,301],
            [515,306],[520,310],[519,316],[528,334],[514,350],[515,358],[504,352],[489,353],
            [485,356],[479,349],[475,353],[468,344],[461,343],[459,337],[449,335],[447,340],
            [444,332],[429,325],[424,314],[423,300],[418,295],[418,283],[422,277],[451,265]
        ]
    },
}

# ─── Transform a country entry ───────────────────────────────────────────────
def transform_country(key, owner_id):
    c = COUNTRIES[key]
    cx, cy = tf(*c['center'])
    dot = tf_dot(c['dotSize'])
    path = [list(tf(*p)) for p in c['path']]
    return {
        'id': c['id'],
        'name': c['name'],
        'ownerId': owner_id,
        'unitsPrecise': c['unitsPrecise'],
        'populationTier': c['populationTier'],
        'center': [cx, cy],
        'dotSize': dot,
        'flagCode': c['flagCode'],
        'path': path,
    }

# ─── Render a country block as JS ────────────────────────────────────────────
def fmt_path(pts, indent='        '):
    rows = []
    for i in range(0, len(pts), 5):
        chunk = pts[i:i+5]
        rows.append(indent + ', '.join(f'[{p[0]},{p[1]}]' for p in chunk))
    return ',\n'.join(rows)

def render_country(c):
    lines = [
        f"      {{",
        f"        id: '{c['id']}', name: '{c['name']}', ownerId: {c['ownerId']},",
        f"        unitsPrecise: {c['unitsPrecise']}, populationTier: {c['populationTier']},",
        f"        center: {{ x: {c['center'][0]}, y: {c['center'][1]} }}, dotSize: {c['dotSize']}, flagCode: '{c['flagCode']}',",
        f"        path: [",
        fmt_path(c['path']),
        f"        ]",
        f"      }}",
    ]
    return '\n'.join(lines)

def render_ai(entries):
    lines = ['    ai: {']
    for i, (d, t, m, w) in enumerate(entries, 1):
        lines.append(f"      {i}: {{ difficulty: '{d}', thinkInterval: {t}, minUnitsToAttack: {m}, focusPlayerWeight: {w} }},")
    lines.append('    },')
    return '\n'.join(lines)

def render_level(num, title, svg, ai_entries, grades, countries, extra=''):
    country_blocks = ',\n'.join(render_country(c) for c in countries)
    g = grades
    extra_line = f'\n    {extra},' if extra else ''
    lines = [
        f'  {num}: {{',
        f"    title: '{title}',",
        f"    svg: '{svg}',",
        render_ai(ai_entries),
        extra_line,
        f"    grades: {{ S: {g['S']}, A: {g['A']}, B: {g['B']}, C: {g['C']} }},",
        f"    countries: [",
        country_blocks,
        f"    ]",
        f"  }}",
    ]
    # remove blank lines from extra_line when empty
    lines = [l for l in lines if l.strip() != '']
    return '\n'.join(lines)

AI_TRES_FACILE = ('tres_facile', 1.2, 12, 0.6)
AI_FACILE      = ('facile', 1, 10, 0.6)
AI_FACILE2     = ('facile', 1.2, 12, 0.5)
GRADES_30      = {'S': 30, 'A': 60, 'B': 90, 'C': 120}

SVG_SOUTH = 'img/europe_south.png'

# ─── Build new level blocks ───────────────────────────────────────────────────

def build_level3():
    countries = [
        transform_country('royaume_uni_lv3', 1),
        transform_country('france_lv3',      2),
        transform_country('espagne_lv3',     3),
        transform_country('pologne_lv3',     4),
    ]
    ai = [AI_FACILE, AI_FACILE, AI_FACILE, AI_FACILE]
    return render_level(3, "Niveau 3 \u2014 Europe de l\\'Ouest et centrale",
                        SVG_SOUTH, ai, GRADES_30, countries)

def build_level4():
    countries = [
        transform_country('france_lv4',      1),
        transform_country('espagne_lv4',     2),
        transform_country('allemagne_lv4',   3),
        transform_country('royaume_uni_lv4', 4),
        transform_country('pologne_lv4',     5),
    ]
    ai = [AI_FACILE, AI_FACILE, AI_FACILE, AI_FACILE, AI_FACILE2]
    return render_level(4, 'Niveau 4 \u2014 Europe',
                        SVG_SOUTH, ai, GRADES_30, countries)

def build_level5():
    # Remove Islande, Suède, Finlande (off-screen on south map)
    countries = [
        transform_country('france_lv5',      1),
        transform_country('italie_lv5',      2),
        transform_country('espagne_lv5',     3),
        transform_country('allemagne_lv5',   4),
        transform_country('royaume_uni_lv5', 5),
        transform_country('pologne_lv5',     6),
    ]
    # Originally 9 AIs (3 Scandi removed → 6 remain)
    ai = [AI_FACILE, AI_FACILE, AI_FACILE, AI_FACILE, AI_FACILE2, AI_FACILE2]
    extra = 'travelSpeed: 90'
    return render_level(5, 'Niveau 5 \u2014 Europe',
                        SVG_SOUTH, ai, GRADES_30, countries, extra=extra)

def build_level6():
    # Same countries as level 5, recomputed from original europe.png coords
    countries = [
        transform_country('france_lv5',      1),
        transform_country('italie_lv5',      2),
        transform_country('espagne_lv5',     3),
        transform_country('allemagne_lv5',   4),
        transform_country('royaume_uni_lv5', 5),
        transform_country('pologne_lv5',     6),
    ]
    ai = [AI_FACILE, AI_FACILE, AI_FACILE, AI_FACILE, AI_FACILE2, AI_FACILE2]
    extra = 'travelSpeed: 90'
    return render_level(6, 'Niveau 6 \u2014 Europe du Sud',
                        SVG_SOUTH, ai, GRADES_30, countries, extra=extra)

# ─── Patch levels.js ─────────────────────────────────────────────────────────
def patch_levels():
    path = os.path.join(BASE, 'levels.js')
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    def find_level_block(num, text):
        """Find the full text of level N: { ... } in text.
        Returns (start_idx, end_idx) of the block including leading newline."""
        # Find '\n  N: {'
        marker = f'\n  {num}: {{'
        start = text.index(marker)
        # Find the next top-level level marker or end of LEVELS object
        next_marker = None
        for n in range(num + 1, 100):
            m = f'\n  {n}: {{'
            try:
                next_marker = text.index(m, start + 1)
                break
            except ValueError:
                continue
        if next_marker is None:
            # Last level → find closing '};' of LEVELS
            end = text.rindex('\n};')
        else:
            end = next_marker
        return start, end

    new_levels = {
        3: build_level3(),
        4: build_level4(),
        5: build_level5(),
        6: build_level6(),
    }

    # Apply patches from highest to lowest to avoid index shifts
    for num in sorted(new_levels.keys(), reverse=True):
        start, end = find_level_block(num, src)
        # The text to insert: '\n  N: { ... },'
        new_text = '\n' + new_levels[num] + ','
        src = src[:start] + new_text + src[end:]
        print(f'Level {num} patched (chars {start}-{end})')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    print('levels.js patched successfully!')

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('=== Computing exact transform ===')
    print(f'tf(285,388) = {tf(285, 388)}  (France expected ~373, ~318)')
    print(f'tf(232,520) = {tf(232, 520)}  (Espagne center)')
    print(f'tf(371,311) = {tf(371, 311)}  (Allemagne center)')
    print(f'tf(215,241) = {tf(215, 241)}  (UK center)')
    print(f'tf(475,314) = {tf(475, 314)}  (Pologne center)')
    print(f'tf(435,493) = {tf(435, 493)}  (Italie center)')
    print()
    print('=== Patching levels.js ===')
    patch_levels()
