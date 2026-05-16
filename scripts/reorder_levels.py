"""
Reorders levels.js from easiest to hardest.

Reorder mapping (new position -> old key):
1->1, 2->2, 3->3, 4->4, 5->5, 6->6, 7->7,
8->14, 9->16, 10->8, 11->15, 12->18, 13->12,
14->13, 15->9, 16->17, 17->10, 18->11
"""

import re

# Line ranges for each level (1-indexed, inclusive)
STARTS = {1:7, 2:85, 3:187, 4:294, 5:388, 6:499, 7:661, 8:854,
          9:917, 10:1020, 11:1180, 12:1381, 13:1490, 14:1615,
          15:1696, 16:1805, 17:1877, 18:2051}
ENDS   = {1:84, 2:186, 3:293, 4:387, 5:498, 6:660, 7:853, 8:916,
          9:1019, 10:1179, 11:1380, 12:1489, 13:1614, 14:1695,
          15:1804, 16:1876, 17:2050, 18:2169}

# New order: new_position -> old_key
ORDER = [1, 2, 3, 4, 5, 6, 7, 14, 16, 8, 15, 18, 12, 13, 9, 17, 10, 11]

# New titles for each new position
NEW_TITLES = {
    1:  "Niveau 1 \u2014 Europe de l'Ouest (3 pays)",
    2:  "Niveau 2 \u2014 Europe de l'Ouest",
    3:  "Niveau 3 \u2014 Europe de l'Ouest et centrale",
    4:  "Niveau 4 \u2014 Europe",
    5:  "Niveau 5 \u2014 Europe",
    6:  "Niveau 6 \u2014 Europe",
    7:  "Niveau 7 \u2014 Europe",
    8:  "Niveau 8 \u2014 Am\u00e9rique du Nord",
    9:  "Niveau 9 \u2014 Asie et Oc\u00e9anie",
    10: "Niveau 10 \u2014 Afrique",
    11: "Niveau 11 \u2014 Am\u00e9rique du Nord",
    12: "Niveau 12 \u2014 Monde",
    13: "Niveau 13 \u2014 Am\u00e9rique du Sud",
    14: "Niveau 14 \u2014 Am\u00e9rique du Sud",
    15: "Niveau 15 \u2014 Afrique",
    16: "Niveau 16 \u2014 Asie et Oc\u00e9anie",
    17: "Niveau 17 \u2014 Afrique",
    18: "Niveau 18 \u2014 Afrique",
}

SRC = r'c:\Users\mguitter\Documents\NW kids wytop\levels.js'
DST = r'c:\Users\mguitter\Documents\NW kids wytop\levels.js'

with open(SRC, 'r', encoding='utf-8') as f:
    all_lines = f.readlines()

# Extract header (before LEVELS object) and footer (after closing brace)
header_lines = all_lines[:5]   # lines 1-5 (comment + const MAX_LEVEL + blank + const LEVELS = {)
# footer is the last few lines after level 18 ends: closing "}" and ";
footer_lines = all_lines[ENDS[18]:]  # line 2169 onward

# Extract each level block as a list of lines (0-indexed)
blocks = {}
for old_key in range(1, 19):
    s = STARTS[old_key] - 1  # 0-indexed
    e = ENDS[old_key]        # exclusive end
    blocks[old_key] = all_lines[s:e]

# Build new file
output_lines = list(header_lines)

for new_pos, old_key in enumerate(ORDER, start=1):
    block = list(blocks[old_key])
    
    # 1. Replace the object key (first line of block): "  14: {" -> "  8: {"
    block[0] = re.sub(r'^\s+\d+:', f'  {new_pos}:', block[0])
    
    # 2. Replace the title string
    new_title = NEW_TITLES[new_pos]
    def replace_title(m):
        # preserve quote style - original uses single quotes
        return f"title: '{new_title}'"
    block_text = ''.join(block)
    block_text = re.sub(r"title: '([^']*)'", f"title: '{new_title}'", block_text, count=1)
    block = block_text.splitlines(keepends=True)
    
    # Add comma separator between levels (all except last)
    output_lines.extend(block)

output_lines.extend(footer_lines)

with open(DST, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(output_lines)

print("Done! Levels reordered successfully.")
print("\nNew order (new level -> original level content):")
for new_pos, old_key in enumerate(ORDER, start=1):
    print(f"  Level {new_pos:2d} -> was old key {old_key:2d}")
