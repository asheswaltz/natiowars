"""
fix_levels.py
- Remove level 6 (duplicate of level 5)
- Renumber levels 7-22 → 6-21, MAX_LEVEL 22→21
- Old level 8 (new level 7): enlarge dots, rename title to include North America
- Fix all empty flagCodes everywhere
"""
import re, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(BASE, 'levels.js')
with open(path, 'r', encoding='utf-8') as f:
    src = f.read()

# ─── 1. Remove level 6 block ─────────────────────────────────────────────────
# Find start of level 6 and end (= start of level 7)
m6 = re.search(r'\n  6: \{', src)
m7 = re.search(r'\n  7: \{', src)
assert m6 and m7, 'Could not find level 6 or 7'
# Remove everything from start of level 6 up to (not including) level 7 marker
src = src[:m6.start()] + src[m7.start():]
print('Level 6 removed')

# ─── 2. Renumber levels 7→6 … 22→21 (in reverse to avoid collisions) ─────────
for n in range(22, 6, -1):
    old = f'\n  {n}: {{'
    new = f'\n  {n-1}: {{'
    assert old in src, f'Could not find level {n}'
    src = src.replace(old, new, 1)
print('Levels renumbered 7-22 → 6-21')

# ─── 3. MAX_LEVEL 22 → 21 ───────────────────────────────────────────────────
src = re.sub(r'(MAX_LEVEL\s*=\s*)22', r'\g<1>21', src)
print('MAX_LEVEL updated to 21')

# ─── 4. Fix empty flagCodes by country id ────────────────────────────────────
FLAG_FIX = {
    'alaska':         'us',
    'amerique_du_sud':'br',
    'amerique_du_nord':'us',
    'oceanie':        'au',
    'afrique':        'za',
    'groenland':      'gl',
}

def fix_empty_flags(text, id_to_flag):
    for cid, flag in id_to_flag.items():
        # Match a block where id: 'alaska' ... flagCode: ''
        # The flagCode '' is within the same entry block
        # Strategy: find the country block start and replace flagCode: '' → flagCode: 'xx'
        pattern = re.compile(
            r"(id:\s*'" + re.escape(cid) + r"'.*?flagCode:\s*)''"
            , re.DOTALL)
        replaced = pattern.sub(r"\g<1>'" + flag + "'", text)
        if replaced != text:
            print(f"  Fixed flagCode for {cid} → {flag}")
        text = replaced
    return text

src = fix_empty_flags(src, FLAG_FIX)

# ─── 5. Enlarge dots for new level 7 (old 8) — North America 3 countries ─────
# This is the 3-country NA level (mexique, canada, alaska) at dot=26
# We target specifically level 7 after renumbering
# Find the level 7 block (from '\n  7: {' to '\n  8: {') and enlarge dots there
m7 = re.search(r'\n  7: \{', src)
m8 = re.search(r'\n  8: \{', src)
assert m7 and m8, 'Could not find new level 7 or 8'
level7_block = src[m7.start():m8.start()]
# Increase dotSize from 26 to 42 only within this block
level7_patched = re.sub(r'dotSize: 26', 'dotSize: 42', level7_block)
src = src[:m7.start()] + level7_patched + src[m8.start():]
print('Level 7 (North America) dots enlarged: 26 → 42')

# ─── 6. Write output ─────────────────────────────────────────────────────────
with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print('\nlevels.js updated.')

# ─── 7. Validate ─────────────────────────────────────────────────────────────
import subprocess, sys
result = subprocess.run(
    ['node', '--input-type=module', '-e',
     "import {readFileSync} from 'fs'; const src=readFileSync('levels.js','utf8');"
     "const F=Function; new F(src+'; return LEVELS;')();"
     "const m=src.match(/MAX_LEVEL\\s*=\\s*(\\d+)/); console.log('OK - MAX_LEVEL='+m[1]);"],
    cwd=BASE, capture_output=True, text=True)
print(result.stdout.strip() or result.stderr.strip())
