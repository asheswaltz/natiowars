"""
split_africa.py — Split Africa levels into Afrique du Nord and Afrique Subsaharienne.

Creates:
  img/afrique_nord.png  — zoomed top half of Africa
  img/afrique_sud.png   — zoomed bottom half of Africa

Patches levels.js:
  Each Africa level (10, 15, 17, 18) is replaced by two levels:
    - Afrique du Nord  (north African countries, rescaled coords)
    - Afrique Subsaharienne  (sub-Saharan countries, rescaled coords)
  Levels 11-18 are renumbered to 12-22 accordingly.
  MAX_LEVEL updated to 22.

Coordinate systems
  Original canvas: 900x600 logical pixels
  afrique.png: 1700x1567 pixels
  cover scale = 900/1700 = 0.529 → rendered height = 829px → top crop = 114.5px
  canvas y=0 ↔ img_y = 114.5/0.529*0.529 + 114.5... actually img_y = 114.5/0.529 ≈ 216.4 ≈ 216

  NORD crop region (canvas): x[170,870], y[0,467]  → 700×467 ≈ 3:2  scale=1.2857
  SUD  crop region (canvas): x[262,900], y[175,600] → 638×425 ≈ 3:2  scale=1.4107

  PNG crops from image:
  NORD: img(321, 216, 1645, 1099)  1324×883
  SUD : img(495, 547, 1700, 1350)  1205×803
"""

import sys, os, re, math
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────
# 1. Generate PNGs
# ─────────────────────────────────────────────────────────────
def make_pngs():
    src = Image.open(os.path.join(BASE, 'img', 'afrique.png'))
    print(f'afrique.png size: {src.size}')

    nord = src.crop((321, 216, 1645, 1099))
    nord = nord.resize((1500, 1000), Image.LANCZOS)
    nord.save(os.path.join(BASE, 'img', 'afrique_nord.png'))
    print(f'afrique_nord.png saved ({nord.size})')

    sud = src.crop((495, 547, 1700, 1350))
    sud = sud.resize((1500, 1000), Image.LANCZOS)
    sud.save(os.path.join(BASE, 'img', 'afrique_sud.png'))
    print(f'afrique_sud.png saved ({sud.size})')

# ─────────────────────────────────────────────────────────────
# 2. Coordinate transforms
# ─────────────────────────────────────────────────────────────
NORD_SCALE = 900 / 700    # 1.2857
NORD_X_OFF = 170
NORD_Y_OFF = 0

SUD_SCALE  = 900 / 638    # 1.4107
SUD_X_OFF  = 262
SUD_Y_OFF  = 175

def tn(x, y):
    return round((x - NORD_X_OFF) * NORD_SCALE), round((y - NORD_Y_OFF) * NORD_SCALE)

def ts(x, y):
    return round((x - SUD_X_OFF) * SUD_SCALE), round((y - SUD_Y_OFF) * SUD_SCALE)

def dot_n(d): return round(d * NORD_SCALE)
def dot_s(d): return round(d * SUD_SCALE)

# ─────────────────────────────────────────────────────────────
# 3. Raw country data (original canvas coords, from levels.js)
# ─────────────────────────────────────────────────────────────
RAW = {
    'algerie': {
        'id': 'algerie', 'name': "Alg\u00e9rie", 'unitsPrecise': 5, 'populationTier': 3, 'flagCode': 'dz',
        'center': [348, 63], 'dotSize': 26,
        'path': [[375,6],[390,9],[390,23],[384,28],[384,32],[399,46],[406,66],[406,90],[403,95],
                 [414,111],[420,110],[428,115],[368,146],[350,149],[335,137],[236,82],[236,74],
                 [241,71],[267,64],[285,55],[288,49],[308,44],[310,40],[302,20],[332,10],[366,10],[374,7]]
    },
    'niger': {
        'id': 'niger', 'name': 'Niger', 'unitsPrecise': 4, 'populationTier': 1, 'flagCode': 'ne',
        'center': [401, 167], 'dotSize': 26,
        'path': [[431,119],[445,121],[451,126],[457,125],[459,133],[466,141],[462,170],[450,178],
                 [446,187],[450,196],[415,196],[405,200],[367,191],[355,194],[349,207],[329,200],
                 [323,192],[323,187],[355,180],[355,176],[361,170],[361,152],[372,150],[430,120]]
    },
    'mali': {
        'id': 'mali', 'name': 'Mali', 'unitsPrecise': 4, 'populationTier': 1, 'flagCode': 'ml',
        'center': [291, 150], 'dotSize': 20,
        'path': [[257,106],[268,106],[331,140],[336,146],[344,148],[346,154],[355,154],[355,169],
                 [346,179],[330,179],[323,183],[306,182],[281,196],[275,195],[262,210],[259,221],
                 [250,219],[242,222],[237,220],[237,214],[227,204],[215,208],[206,205],[200,189],
                 [204,184],[214,186],[224,183],[265,181],[267,174],[264,167],[258,107]]
    },
    'egypte': {
        'id': 'egypte', 'name': 'Egypte', 'unitsPrecise': 9, 'populationTier': 4, 'flagCode': 'eg',
        'center': [609, 74], 'dotSize': 20,
        'path': [[558,52],[587,58],[602,53],[614,53],[618,58],[622,55],[639,56],[645,67],[640,79],
                 [625,62],[620,66],[640,95],[656,112],[656,119],[666,126],[561,126],[558,73],
                 [554,63],[554,54],[557,53]]
    },
    'soudan': {
        'id': 'soudan', 'name': 'Soudan', 'unitsPrecise': 6, 'populationTier': 2, 'flagCode': 'sd',
        'center': [597, 194], 'dotSize': 22,
        'path': [[561,130],[671,130],[675,150],[686,161],[673,168],[668,199],[650,221],[645,218],
                 [645,207],[636,205],[628,209],[631,216],[623,225],[611,220],[599,228],[579,227],
                 [572,220],[563,220],[552,234],[549,231],[551,224],[544,217],[536,201],[540,192],
                 [539,186],[543,181],[553,180],[551,146],[562,145],[561,131]]
    },
    'libye': {
        'id': 'libye', 'name': 'Libye', 'unitsPrecise': 5, 'populationTier': 2, 'flagCode': 'ly',
        'center': [473, 73], 'dotSize': 26,
        'path': [[425,39],[455,44],[463,54],[496,63],[509,55],[506,49],[508,46],[520,41],[525,41],
                 [533,47],[550,50],[548,64],[552,77],[556,142],[545,144],[470,114],[453,121],
                 [449,117],[434,114],[422,105],[417,106],[410,96],[413,72],[409,59],[413,56],
                 [413,51],[424,44],[425,40]]
    },
    'arabie_saoudite': {
        'id': 'arabie_saoudite', 'name': 'Arabie saoudite', 'unitsPrecise': 5, 'populationTier': 2, 'flagCode': 'sa',
        'center': [741, 106], 'dotSize': 26,
        'path': [[686,48],[706,53],[741,72],[766,73],[770,77],[776,77],[781,84],[794,91],[795,98],
                 [804,108],[810,110],[817,122],[850,126],[848,142],[822,150],[792,153],[785,156],
                 [776,166],[739,161],[734,168],[732,167],[718,149],[698,133],[697,123],[691,114],
                 [680,108],[662,85],[650,76],[651,71],[660,72],[679,60],[671,52],[685,49]]
    },
    'madagascar': {
        'id': 'madagascar', 'name': 'Madagascar', 'unitsPrecise': 5, 'populationTier': 1, 'flagCode': 'mg',
        'center': [772, 467], 'dotSize': 20,
        'path': [[799,408],[804,415],[807,430],[803,429],[799,433],[800,441],[768,506],[754,511],
                 [743,508],[738,484],[751,466],[749,446],[753,440],[769,437],[783,428],[799,409]]
    },
    'afrique_du_sud': {
        'id': 'afrique_du_sud', 'name': 'Afrique du Sud', 'unitsPrecise': 6, 'populationTier': 2, 'flagCode': 'za',
        'center': [557, 532], 'dotSize': 20,
        'path': [[600,488],[615,489],[620,501],[619,511],[611,514],[607,524],[614,530],[626,526],
                 [621,538],[613,542],[599,557],[577,572],[556,579],[528,578],[504,586],[490,580],
                 [491,562],[476,540],[477,537],[480,542],[502,542],[509,537],[510,513],[515,526],
                 [525,525],[539,514],[548,517],[562,516],[581,498],[599,489]]
    },
    'angola': {
        'id': 'angola', 'name': 'Angola', 'unitsPrecise': 5, 'populationTier': 2, 'flagCode': 'ao',
        'center': [491, 398], 'dotSize': 26,
        'path': [[447,356],[475,356],[487,374],[505,373],[512,366],[527,368],[530,374],[528,381],
                 [531,386],[531,397],[549,397],[548,409],[530,409],[528,412],[527,437],[537,447],
                 [509,449],[495,444],[454,445],[447,441],[433,443],[441,417],[454,402],[454,393],
                 [446,381],[449,373],[440,357],[446,357]]
    },
    'rd_congo': {
        'id': 'rd_congo', 'name': 'RD Congo', 'unitsPrecise': 9, 'populationTier': 1, 'flagCode': 'cd',
        'center': [544, 333], 'dotSize': 24,
        'path': [[568,266],[585,267],[596,274],[608,272],[618,279],[619,289],[611,296],[600,326],
                 [602,356],[612,371],[596,375],[593,403],[587,403],[583,398],[571,400],[567,396],
                 [551,392],[537,393],[532,363],[514,360],[506,362],[502,368],[490,369],[477,351],
                 [442,351],[453,345],[459,349],[477,336],[480,322],[494,310],[496,292],[505,270],
                 [509,268],[537,276],[542,271],[566,268]]
    },
    'ethiopie': {
        'id': 'ethiopie', 'name': 'Ethiopie', 'unitsPrecise': 10, 'populationTier': 3, 'flagCode': 'et',
        'center': [704, 234], 'dotSize': 26,
        'path': [[689,189],[715,193],[728,205],[723,211],[724,217],[732,219],[743,233],[780,244],
                 [759,263],[745,264],[729,272],[718,269],[703,276],[694,275],[682,268],[674,268],
                 [670,260],[646,241],[654,237],[655,222],[672,204],[675,192],[686,193],[688,190]]
    },
    'tanzanie': {
        'id': 'tanzanie', 'name': 'Tanzanie', 'unitsPrecise': 7, 'populationTier': 2, 'flagCode': 'tz',
        'center': [654, 349], 'dotSize': 26,
        'path': [[622,317],[628,317],[626,326],[630,330],[648,328],[652,325],[649,321],[655,318],
                 [685,332],[689,339],[700,345],[695,355],[702,363],[700,377],[708,390],[683,398],
                 [661,397],[659,387],[652,381],[625,374],[620,362],[613,356],[612,345],[623,334],[623,318]]
    },
    'namibie': {
        'id': 'namibie', 'name': 'Namibie', 'unitsPrecise': 3, 'populationTier': 2, 'flagCode': 'na',
        'center': [472, 483], 'dotSize': 23,
        'path': [[439,446],[447,446],[453,450],[494,449],[500,453],[517,454],[515,481],[508,481],
                 [505,486],[503,536],[490,539],[484,538],[479,532],[471,534],[467,530],[460,511],
                 [458,487],[446,471],[442,460],[434,452],[434,448],[438,447]]
    },
}

# ─────────────────────────────────────────────────────────────
# 4. Build transformed country JS block
# ─────────────────────────────────────────────────────────────
def fmt_path(pts, indent='          '):
    """Format a path list with up to 5 points per line."""
    rows = []
    for i in range(0, len(pts), 5):
        chunk = pts[i:i+5]
        rows.append(indent + ', '.join(f'[{p[0]},{p[1]}]' for p in chunk))
    return ',\n'.join(rows)

def country_block(key, owner_id, tf_center, tf_dot, tf_path, indent='      '):
    r = RAW[key]
    cx, cy = tf_center
    lines = []
    lines.append(f'{indent}{{')
    lines.append(f"{indent}  id: '{r['id']}', name: '{r['name']}', ownerId: {owner_id},")
    lines.append(f"{indent}  unitsPrecise: {r['unitsPrecise']}, populationTier: {r['populationTier']},")
    lines.append(f"{indent}  center: {{ x: {cx}, y: {cy} }}, dotSize: {tf_dot}, flagCode: '{r['flagCode']}',")
    lines.append(f"{indent}  path: [")
    lines.append(fmt_path(tf_path, indent + '    '))
    lines.append(f"{indent}  ]")
    lines.append(f'{indent}}}')
    return '\n'.join(lines)

def build_country_nord(key, owner_id):
    r = RAW[key]
    cx, cy = tn(*r['center'])
    dot = dot_n(r['dotSize'])
    path = [list(tn(*p)) for p in r['path']]
    return country_block(key, owner_id, (cx, cy), dot, path)

def build_country_sud(key, owner_id):
    r = RAW[key]
    cx, cy = ts(*r['center'])
    dot = dot_s(r['dotSize'])
    path = [list(ts(*p)) for p in r['path']]
    return country_block(key, owner_id, (cx, cy), dot, path)

# ─────────────────────────────────────────────────────────────
# 5. AI config builder
# ─────────────────────────────────────────────────────────────
# AI difficulty presets
AI_EASY   = ('facile', 1,   10, 0.6)
AI_EASY2  = ('facile', 1.2, 12, 0.5)
AI_MEDIUM = ('moyen',  0.8,  9, 0.6)

def ai_entry(n, diff, interval, minUnits, weight):
    return (f"      {n}: {{ difficulty: '{diff}', thinkInterval: {interval}, "
            f"minUnitsToAttack: {minUnits}, focusPlayerWeight: {weight} }}")

def build_ai(entries):
    """entries = list of (difficulty, thinkInterval, minUnits, weight)"""
    lines = ['    ai: {']
    for i, (d, t, m, w) in enumerate(entries, 1):
        lines.append(ai_entry(i, d, t, m, w))
    lines.append('    },')
    return '\n'.join(lines)

# ─────────────────────────────────────────────────────────────
# 6. Level builder
# ─────────────────────────────────────────────────────────────
def build_level(num, title, svg, ai_entries, grades, countries_js):
    s = grades['S']; a = grades['A']; b = grades['B']; c = grades['C']
    lines = [
        f'  {num}: {{',
        f"    title: '{title}',",
        f"    svg: '{svg}',",
        build_ai(ai_entries),
        f"    grades: {{ S: {s}, A: {a}, B: {b}, C: {c} }},",
        f"    countries: [",
        countries_js,
        f"    ]",
        f"  }}",
    ]
    return '\n'.join(lines)

def join_countries(country_blocks):
    return ',\n'.join(country_blocks)

# ─────────────────────────────────────────────────────────────
# 7. Build all split Africa levels
# ─────────────────────────────────────────────────────────────
GRADES_STD = {'S': 20, 'A': 60, 'B': 90, 'C': 120}

# ── Level 10 split ──────────────────────────────────────────
# Original: Madagascar(S), Algérie(N), Afrique du Sud(S), Niger(N)
def make_lvl10_nord(num):
    countries = [
        build_country_nord('algerie', 1),
        build_country_nord('niger',   2),
    ]
    ai = [AI_MEDIUM, AI_EASY]
    return build_level(num, 'Niveau {n} \u2014 Afrique du Nord'.format(n=num),
                       'img/afrique_nord.png', ai, GRADES_STD, join_countries(countries))

def make_lvl10_sud(num):
    countries = [
        build_country_sud('madagascar',   1),
        build_country_sud('afrique_du_sud', 2),
    ]
    ai = [AI_MEDIUM, AI_EASY]
    return build_level(num, 'Niveau {n} \u2014 Afrique Subsaharienne'.format(n=num),
                       'img/afrique_sud.png', ai, GRADES_STD, join_countries(countries))

# ── Level 15 split ──────────────────────────────────────────
# Original: Madagascar(S), Algérie(N), AfSud(S), Niger(N), Mali(N), Egypte(N), Soudan(N)
def make_lvl15_nord(num):
    countries = [
        build_country_nord('mali',    1),
        build_country_nord('algerie', 2),
        build_country_nord('niger',   3),
        build_country_nord('egypte',  4),
        build_country_nord('soudan',  5),
    ]
    ai = [AI_MEDIUM, AI_EASY, AI_EASY, AI_EASY, AI_EASY2]
    return build_level(num, 'Niveau {n} \u2014 Afrique du Nord'.format(n=num),
                       'img/afrique_nord.png', ai, GRADES_STD, join_countries(countries))

def make_lvl15_sud(num):
    countries = [
        build_country_sud('madagascar',    1),
        build_country_sud('afrique_du_sud', 2),
    ]
    ai = [AI_MEDIUM, AI_EASY]
    return build_level(num, 'Niveau {n} \u2014 Afrique Subsaharienne'.format(n=num),
                       'img/afrique_sud.png', ai, GRADES_STD, join_countries(countries))

# ── Level 17 split ──────────────────────────────────────────
# Original: idem lvl15 + Angola(S), RDCongo(S), Ethiopie(S), Tanzanie(S)
def make_lvl17_nord(num):
    countries = [
        build_country_nord('mali',    1),
        build_country_nord('algerie', 2),
        build_country_nord('niger',   3),
        build_country_nord('egypte',  4),
        build_country_nord('soudan',  5),
    ]
    ai = [AI_MEDIUM, AI_EASY, AI_EASY, AI_EASY, AI_EASY2]
    return build_level(num, 'Niveau {n} \u2014 Afrique du Nord'.format(n=num),
                       'img/afrique_nord.png', ai, GRADES_STD, join_countries(countries))

def make_lvl17_sud(num):
    countries = [
        build_country_sud('angola',      1),
        build_country_sud('rd_congo',    2),
        build_country_sud('ethiopie',    3),
        build_country_sud('tanzanie',    4),
        build_country_sud('madagascar',  5),
        build_country_sud('afrique_du_sud', 6),
    ]
    ai = [AI_MEDIUM, AI_EASY, AI_EASY, AI_EASY, AI_EASY2, AI_EASY2]
    return build_level(num, 'Niveau {n} \u2014 Afrique Subsaharienne'.format(n=num),
                       'img/afrique_sud.png', ai, GRADES_STD, join_countries(countries))

# ── Level 18 split ──────────────────────────────────────────
# Original: idem lvl17 + Namibie(S) + Arabie saoudite(N) + Libye(N)
def make_lvl18_nord(num):
    countries = [
        build_country_nord('mali',             1),
        build_country_nord('algerie',          2),
        build_country_nord('libye',            3),
        build_country_nord('niger',            4),
        build_country_nord('egypte',           5),
        build_country_nord('soudan',           6),
        build_country_nord('arabie_saoudite',  7),
    ]
    ai = [AI_MEDIUM, AI_EASY, AI_EASY, AI_EASY, AI_EASY, AI_EASY2, AI_EASY2]
    return build_level(num, 'Niveau {n} \u2014 Afrique du Nord'.format(n=num),
                       'img/afrique_nord.png', ai, GRADES_STD, join_countries(countries))

def make_lvl18_sud(num):
    countries = [
        build_country_sud('angola',        1),
        build_country_sud('rd_congo',      2),
        build_country_sud('ethiopie',      3),
        build_country_sud('tanzanie',      4),
        build_country_sud('namibie',       5),
        build_country_sud('madagascar',    6),
        build_country_sud('afrique_du_sud', 7),
    ]
    ai = [AI_MEDIUM, AI_EASY, AI_EASY, AI_EASY, AI_EASY2, AI_EASY2, AI_EASY2]
    return build_level(num, 'Niveau {n} \u2014 Afrique Subsaharienne'.format(n=num),
                       'img/afrique_sud.png', ai, GRADES_STD, join_countries(countries))

# ─────────────────────────────────────────────────────────────
# 8. Parse levels.js and rebuild
# ─────────────────────────────────────────────────────────────
def parse_levels(src):
    """Extract a dict of {level_num: js_block_text} from the LEVELS object.
    Returns (header, levels_dict, footer).
    header = everything before '  1: {'
    footer = everything after the last level's closing '  }'
    """
    # Find start of LEVELS object content
    levels_start = src.index('const LEVELS = {')
    # Split into (before_levels, levels_body)
    # Find the first level key '  1: {'
    idx_first = src.index('\n  1: {', levels_start)
    header = src[:idx_first]  # up to (not including) \n  1: {

    # Find the closing '};\n' of the LEVELS object
    # It's the very last '};\n' in the file
    levels_end = src.rindex('\n};')
    footer = src[levels_end:]  # includes '\n};\n'

    body = src[idx_first:levels_end]  # '\n  1: { ... }'

    # Split by '\n  N: {' where N is 1..99
    pattern = re.compile(r'\n(?=  \d+: \{)')
    blocks_raw = pattern.split(body)
    # blocks_raw[0] is '' (empty before first match), then each block starts with '  N: {'
    blocks = [b for b in blocks_raw if b.strip()]

    levels_dict = {}
    for block in blocks:
        m = re.match(r'\s*(\d+): \{', block)
        if m:
            n = int(m.group(1))
            levels_dict[n] = block.rstrip(',').rstrip()
            # Remove trailing comma from last line of block if present
            # We keep raw text; commas are added during reconstruction

    return header, levels_dict, footer


def rebuild_levels(header, levels_seq, footer):
    """
    levels_seq = list of (num, js_text) tuples (already numbered correctly)
    js_text does NOT have a trailing comma.
    """
    lines = [header]
    for i, (num, text) in enumerate(levels_seq):
        is_last = (i == len(levels_seq) - 1)
        # Ensure the text has the correct number
        # text is already correctly numbered (from build_level)
        entry = '  ' + text.strip() if not text.startswith('  ') else text
        if not is_last:
            lines.append('\n' + entry + ',')
        else:
            lines.append('\n' + entry)
    lines.append(footer)
    return ''.join(lines)


def patch_levels_js():
    path = os.path.join(BASE, 'levels.js')
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    header, levels_dict, footer = parse_levels(src)

    # Africa level keys that need splitting
    AFRICA_LEVELS = {10, 15, 17, 18}

    # Build final sequence: walk 1..18, insert splits for Africa levels
    # New numbering after insertions:
    #   1-9  → 1-9
    #   10N  → 10, 10S → 11  (+1 shift from here)
    #   old11→12, old12→13, old13→14, old14→15
    #   15N  → 16, 15S → 17  (+1 more shift)
    #   old16→18
    #   17N  → 19, 17S → 20  (+1 more shift)
    #   18N  → 21, 18S → 22  (+1 more shift)
    # Total = 22 levels

    new_levels = []   # list of (new_num, js_text)
    new_num = 0

    SPLIT_BUILDERS = {
        10: (make_lvl10_nord, make_lvl10_sud),
        15: (make_lvl15_nord, make_lvl15_sud),
        17: (make_lvl17_nord, make_lvl17_sud),
        18: (make_lvl18_nord, make_lvl18_sud),
    }

    for old_num in sorted(levels_dict.keys()):
        if old_num in AFRICA_LEVELS:
            # Insert NORD level
            new_num += 1
            nord_text = SPLIT_BUILDERS[old_num][0](new_num)
            new_levels.append((new_num, nord_text))
            # Insert SUD level
            new_num += 1
            sud_text = SPLIT_BUILDERS[old_num][1](new_num)
            new_levels.append((new_num, sud_text))
        else:
            # Renumber existing level
            new_num += 1
            old_text = levels_dict[old_num]
            # Replace the level number at the start: '  10: {' → '  12: {'
            new_text = re.sub(r'^\s*\d+: \{', f'  {new_num}: {{', old_text, count=1)
            # Also update the title "Niveau XX —" if present
            new_text = re.sub(
                r"(title: 'Niveau )\d+( )",
                lambda m: m.group(1) + str(new_num) + m.group(2),
                new_text, count=1
            )
            new_levels.append((new_num, new_text))

    total = new_num
    print(f'New total levels: {total}')

    # Update MAX_LEVEL
    new_header = re.sub(r'const MAX_LEVEL = \d+;', f'const MAX_LEVEL = {total};', header)

    result = rebuild_levels(new_header, new_levels, footer)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(result)
    print('levels.js patched successfully!')
    return total


# ─────────────────────────────────────────────────────────────
# 9. Main
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('=== Step 1: Generate PNG crops ===')
    make_pngs()

    print('\n=== Step 2: Patch levels.js ===')
    total = patch_levels_js()

    print(f'\nDone! Africa split complete. Game now has {total} levels.')
    print('New background images: img/afrique_nord.png, img/afrique_sud.png')
