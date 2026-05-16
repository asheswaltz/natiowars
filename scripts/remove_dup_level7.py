"""Remove the duplicate old Level 7 (Niveau 7 — Europe) from levels.js."""
import re

LEVELS_PATH = r'c:\Users\mguitter\Documents\NW kids wytop\levels.js'

with open(LEVELS_PATH, 'r', encoding='utf-8') as f:
    src = f.read()

# The old level 7 looks like:  },\n  7: {\n    title: 'Niveau 7 — Europe'
# Find it and remove through to right before "  8: {"
# We want to match the comma+newline before it too
pat = re.compile(
    r',\n  7: \{\n    title: \'Niveau 7 \u2014 Europe\'.*?(?=  8: \{)',
    re.DOTALL
)

m = pat.search(src)
if not m:
    print("Old Level 7 Europe block not found — already removed?")
else:
    print(f"Found old Level 7 Europe at chars {m.start()}-{m.end()}, removing...")
    src = src[:m.start()] + ',\n' + src[m.end():]
    with open(LEVELS_PATH, 'w', encoding='utf-8') as f:
        f.write(src)
    print("Done!")
