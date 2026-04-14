import os

def fix_cli():
    path = os.path.join('src', 'mongo_setup', 'cli.py')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix broken symbols
    replacements = {
        'â¬†': '+',
        'â†’': '->',
        'âœ—': 'x',
        'â–¸': '>',
        'âœ“': '+',
        'ðŸ§©': 'RESOURCE',
        'ðŸš€': 'ROCKET',
        'ðŸ”': 'LOCK',
        'ðŸ ³': 'DOKCER',
        'ðŸ§ª': 'TEST',
        'ðŸ“¦': 'PROJECT'
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    # Also fix some other likely ones that might appear (like the ones from my previous edits)
    # The user screenshot showed âœ“ specifically.
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_cli()
