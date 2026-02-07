#!/usr/bin/env python3
"""
Update README.md with Minesweeper game board section
"""

import re

# Read files
with open('MINESWEEPER.md', 'r', encoding='utf-8') as f:
    minesweeper_content = f.read()

with open('README.md', 'r', encoding='utf-8') as f:
    readme_content = f.read()

# Pattern to find existing minesweeper section
pattern = r'<!-- MINESWEEPER:START -->.*?<!-- MINESWEEPER:END -->'
replacement = f'<!-- MINESWEEPER:START -->\n{minesweeper_content}\n<!-- MINESWEEPER:END -->'

if '<!-- MINESWEEPER:START -->' in readme_content:
    # Replace existing section
    new_readme = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
else:
    # Add section after the header
    # Find the first </div> and insert after it
    insert_pos = readme_content.find('</div>') + len('</div>')
    new_readme = readme_content[:insert_pos] + '\n\n' + replacement + '\n' + readme_content[insert_pos:]

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(new_readme)

print("README.md updated with game board")
