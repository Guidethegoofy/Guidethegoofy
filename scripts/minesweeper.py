#!/usr/bin/env python3
"""
Minesweeper Game for GitHub README
Generates an interactive game board that can be played via GitHub Actions
"""

import json
import random
import sys
import os
import io

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Constants
BOARD_SIZE = 8
MINES_COUNT = 10
CELL_SIZE = 40
PADDING = 2

# Tokyo Night color theme
COLORS = {
    'bg': '#1a1b26',
    'hidden': '#24283b',
    'hidden_hover': '#2f3549',
    'revealed': '#1a1b26',
    'border': '#414868',
    'text': '#c0caf5',
    'mine': '#f7768e',
    'flag': '#ff9e64',
    'numbers': {
        1: '#7aa2f7',  # blue
        2: '#9ece6a',  # green
        3: '#f7768e',  # red
        4: '#bb9af7',  # purple
        5: '#e0af68',  # orange
        6: '#7dcfff',  # cyan
        7: '#c0caf5',  # white
        8: '#565f89',  # gray
    }
}

def load_game_state():
    """Load game state from JSON file"""
    state_file = os.path.join(os.path.dirname(__file__), '..', 'game_state.json')
    try:
        with open(state_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return create_new_game()

def save_game_state(state):
    """Save game state to JSON file"""
    state_file = os.path.join(os.path.dirname(__file__), '..', 'game_state.json')
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def create_new_game():
    """Create a new game state"""
    state = {
        'board_size': BOARD_SIZE,
        'mines_count': MINES_COUNT,
        'board': [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'revealed': [[False for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'flagged': [[False for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'game_over': False,
        'won': False,
        'moves_count': 0,
        'last_move': None,
        'initialized': False
    }
    return state

def initialize_board(state, first_row, first_col):
    """Place mines avoiding the first clicked cell"""
    board = state['board']
    size = state['board_size']
    mines = state['mines_count']
    
    # Get all possible positions except first click and neighbors
    safe_zone = set()
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = first_row + dr, first_col + dc
            if 0 <= nr < size and 0 <= nc < size:
                safe_zone.add((nr, nc))
    
    possible_positions = [
        (r, c) for r in range(size) for c in range(size)
        if (r, c) not in safe_zone
    ]
    
    # Place mines
    mine_positions = random.sample(possible_positions, min(mines, len(possible_positions)))
    for r, c in mine_positions:
        board[r][c] = -1  # -1 represents a mine
    
    # Calculate numbers
    for r in range(size):
        for c in range(size):
            if board[r][c] == -1:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == -1:
                        count += 1
            board[r][c] = count
    
    state['initialized'] = True
    return state

def reveal_cell(state, row, col):
    """Reveal a cell and cascade if empty"""
    if state['game_over'] or state['won']:
        return state
    
    if state['revealed'][row][col] or state['flagged'][row][col]:
        return state
    
    # Initialize board on first click
    if not state['initialized']:
        state = initialize_board(state, row, col)
    
    state['revealed'][row][col] = True
    state['moves_count'] += 1
    state['last_move'] = f"{chr(65 + col)}{row + 1}"
    
    # Check if mine
    if state['board'][row][col] == -1:
        state['game_over'] = True
        # Reveal all mines
        for r in range(state['board_size']):
            for c in range(state['board_size']):
                if state['board'][r][c] == -1:
                    state['revealed'][r][c] = True
        return state
    
    # Cascade reveal for empty cells
    if state['board'][row][col] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < state['board_size'] and 0 <= nc < state['board_size']:
                    if not state['revealed'][nr][nc]:
                        state = reveal_cell(state, nr, nc)
    
    # Check win condition
    state = check_win(state)
    return state

def toggle_flag(state, row, col):
    """Toggle flag on a cell"""
    if state['game_over'] or state['won']:
        return state
    
    if state['revealed'][row][col]:
        return state
    
    state['flagged'][row][col] = not state['flagged'][row][col]
    state['last_move'] = f"🚩{chr(65 + col)}{row + 1}"
    return state

def check_win(state):
    """Check if player has won"""
    for r in range(state['board_size']):
        for c in range(state['board_size']):
            # If there's an unrevealed non-mine cell, game continues
            if not state['revealed'][r][c] and state['board'][r][c] != -1:
                return state
    state['won'] = True
    return state

def generate_svg(state):
    """Generate SVG image of the game board"""
    size = state['board_size']
    width = size * CELL_SIZE + PADDING * 2
    height = size * CELL_SIZE + PADDING * 2 + 30  # Extra space for header
    
    svg_parts = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'  <defs>',
        f'    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">',
        f'      <feDropShadow dx="1" dy="1" stdDeviation="1" flood-opacity="0.3"/>',
        f'    </filter>',
        f'  </defs>',
        f'  <rect width="{width}" height="{height}" fill="{COLORS["bg"]}"/>',
    ]
    
    # Header
    status = "💥 GAME OVER!" if state['game_over'] else ("🎉 YOU WIN!" if state['won'] else "🎯 MINESWEEPER")
    mines_left = state['mines_count'] - sum(sum(row) for row in state['flagged'])
    svg_parts.append(f'  <text x="{width//2}" y="20" font-family="monospace" font-size="14" fill="{COLORS["text"]}" text-anchor="middle">{status} | 💣 {mines_left} | Moves: {state["moves_count"]}</text>')
    
    # Draw cells
    for r in range(size):
        for c in range(size):
            x = PADDING + c * CELL_SIZE
            y = PADDING + r * CELL_SIZE + 25
            
            if state['revealed'][r][c]:
                # Revealed cell
                svg_parts.append(f'  <rect x="{x}" y="{y}" width="{CELL_SIZE-2}" height="{CELL_SIZE-2}" fill="{COLORS["revealed"]}" stroke="{COLORS["border"]}" stroke-width="1" rx="4"/>')
                
                value = state['board'][r][c]
                if value == -1:
                    # Mine
                    svg_parts.append(f'  <text x="{x + CELL_SIZE//2}" y="{y + CELL_SIZE//2 + 5}" font-size="20" text-anchor="middle">💣</text>')
                elif value > 0:
                    # Number
                    color = COLORS['numbers'].get(value, COLORS['text'])
                    svg_parts.append(f'  <text x="{x + CELL_SIZE//2}" y="{y + CELL_SIZE//2 + 6}" font-family="monospace" font-size="18" font-weight="bold" fill="{color}" text-anchor="middle">{value}</text>')
            else:
                # Hidden cell
                svg_parts.append(f'  <rect x="{x}" y="{y}" width="{CELL_SIZE-2}" height="{CELL_SIZE-2}" fill="{COLORS["hidden"]}" stroke="{COLORS["border"]}" stroke-width="1" rx="4" filter="url(#shadow)"/>')
                
                if state['flagged'][r][c]:
                    svg_parts.append(f'  <text x="{x + CELL_SIZE//2}" y="{y + CELL_SIZE//2 + 5}" font-size="18" text-anchor="middle">🚩</text>')
    
    # Column labels
    for c in range(size):
        x = PADDING + c * CELL_SIZE + CELL_SIZE // 2
        svg_parts.append(f'  <text x="{x}" y="{height - 5}" font-family="monospace" font-size="10" fill="{COLORS["border"]}" text-anchor="middle">{chr(65 + c)}</text>')
    
    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)

def generate_readme_section(state, repo_owner="Guidethegoofy", repo_name="Guidethegoofy"):
    """Generate markdown section for README with clickable links"""
    lines = []
    lines.append('<div align="center">')
    lines.append('')
    lines.append('## 🎯 Minesweeper')
    lines.append('')
    lines.append('![Minesweeper Board](minesweeper.svg)')
    lines.append('')
    
    if state['game_over']:
        lines.append('**💥 Game Over!** Click "New Game" to play again.')
        lines.append('')
    elif state['won']:
        lines.append('**🎉 Congratulations! You won!** Click "New Game" to play again.')
        lines.append('')
    else:
        lines.append('**Click a cell coordinate below to reveal it!**')
        lines.append('')
    
    # Generate clickable grid
    lines.append('|   | ' + ' | '.join([chr(65 + c) for c in range(state['board_size'])]) + ' |')
    lines.append('|---' + '|---' * state['board_size'] + '|')
    
    for r in range(state['board_size']):
        row_cells = [f'**{r + 1}**']
        for c in range(state['board_size']):
            cell_name = f"{chr(65 + c)}{r + 1}"
            if state['revealed'][r][c]:
                value = state['board'][r][c]
                if value == -1:
                    row_cells.append('💣')
                elif value == 0:
                    row_cells.append('·')
                else:
                    row_cells.append(str(value))
            elif state['flagged'][r][c]:
                row_cells.append('🚩')
            else:
                # Clickable link to workflow
                workflow_url = f"https://github.com/{repo_owner}/{repo_name}/actions/workflows/main.yml"
                row_cells.append(f'[▪]({workflow_url})')
        lines.append('| ' + ' | '.join(row_cells) + ' |')
    
    lines.append('')
    lines.append(f'📊 **Moves:** {state["moves_count"]} | 💣 **Mines:** {state["mines_count"]} | 🚩 **Flags:** {sum(sum(row) for row in state["flagged"])}')
    lines.append('')
    lines.append('> 💡 **How to play:** Go to [Actions](https://github.com/{}/{}/actions) → "Minesweeper Game" → "Run workflow" → Enter cell (e.g., A1)'.format(repo_owner, repo_name))
    lines.append('')
    lines.append('</div>')
    
    return '\n'.join(lines)

def parse_cell(cell_str):
    """Parse cell string like 'A1' to (row, col)"""
    cell_str = cell_str.strip().upper()
    if len(cell_str) < 2:
        return None, None
    
    col = ord(cell_str[0]) - ord('A')
    try:
        row = int(cell_str[1:]) - 1
    except ValueError:
        return None, None
    
    return row, col

def main():
    if len(sys.argv) < 2:
        print("Usage: python minesweeper.py <action> [cell]")
        print("Actions: reveal, flag, new, render")
        print("Example: python minesweeper.py reveal A1")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    state = load_game_state()
    
    if action == 'new':
        state = create_new_game()
        print("[GAME] New game created!")
    
    elif action == 'reveal':
        if len(sys.argv) < 3:
            print("Error: Cell required for reveal action")
            sys.exit(1)
        row, col = parse_cell(sys.argv[2])
        if row is None or col is None:
            print(f"Error: Invalid cell '{sys.argv[2]}'")
            sys.exit(1)
        if not (0 <= row < state['board_size'] and 0 <= col < state['board_size']):
            print(f"Error: Cell out of bounds")
            sys.exit(1)
        state = reveal_cell(state, row, col)
        print(f"[OK] Revealed cell {sys.argv[2].upper()}")
    
    elif action == 'flag':
        if len(sys.argv) < 3:
            print("Error: Cell required for flag action")
            sys.exit(1)
        row, col = parse_cell(sys.argv[2])
        if row is None or col is None:
            print(f"Error: Invalid cell '{sys.argv[2]}'")
            sys.exit(1)
        if not (0 <= row < state['board_size'] and 0 <= col < state['board_size']):
            print(f"Error: Cell out of bounds")
            sys.exit(1)
        state = toggle_flag(state, row, col)
        print(f"[FLAG] Toggled flag on cell {sys.argv[2].upper()}")
    
    elif action == 'render':
        print("[RENDER] Rendering board...")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
    
    # Save state
    save_game_state(state)
    
    # Generate SVG
    svg_content = generate_svg(state)
    svg_file = os.path.join(os.path.dirname(__file__), '..', 'minesweeper.svg')
    with open(svg_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"[FILE] Updated minesweeper.svg")
    
    # Generate README section
    readme_section = generate_readme_section(state)
    readme_file = os.path.join(os.path.dirname(__file__), '..', 'MINESWEEPER.md')
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_section)
    print(f"[FILE] Updated MINESWEEPER.md")
    
    if state['game_over']:
        print("[GAME OVER] You hit a mine!")
    elif state['won']:
        print("[WIN] Congratulations, you won!")

if __name__ == '__main__':
    main()
