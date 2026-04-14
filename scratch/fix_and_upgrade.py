import os
import re

def fix_and_upgrade():
    path = os.path.join('src', 'mongo_setup', 'cli.py')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add subprocess import
    if "import subprocess" not in content:
        content = "import subprocess\n" + content

    # Upgrade version
    content = content.replace('__version__ = "0.8.0"', '__version__ = "0.8.1"')

    # Fix ALL symbols including Unicode that might be misinterpreted
    replacements = {
        'â¬†': '+',
        'â†’': '->',
        'âœ—': 'x',
        'â–¸': '>',
        'âœ“': '+',
        'ðŸ§©': '[RESOURCE]',
        'ðŸš€': '[SETUP]',
        'ðŸ”': '[AUTH]',
        'ðŸ ³': '[DOCKER]',
        'ðŸ§ª': '[TEST]',
        'ðŸ“¦': '[BUILDING]',
        'âœ…': '[DONE]',
        '✓': '+',
        '→': '>',
        '🚀': '[ROCKET]',
        '🔐': '[AUTH]',
        '🐳': '[DOCKER]',
        '🧪': '[TEST]',
        '📦': '[BUILDING]',
        '🧩': '[COMPONENTS]',
        '✅': '[DONE]'
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)

    # Insert auto-start logic before if __name__ == "__main__":
    auto_start_code = """
    # =============================================
    # AUTO-START SERVER
    # =============================================
    if args.command == "setup" or (not args.command and not include_resource):
        start_answer = console.input("\\n  [bold cyan]▸ Start the server now? [dim](y/N)[/dim]: ").strip().lower()
        if start_answer in ("y", "yes"):
            console.print("\\n  [bold cyan]▸ Starting FastAPI server...[/bold cyan]")
            try:
                if include_docker:
                    subprocess.run(["docker-compose", "up", "--build"], shell=(os.name == 'nt'))
                else:
                    # Install dependencies if needed? Maybe just tell user to do it.
                    # But the user asked for "automaticly needs to stert".
                    # Let's try running main.py directly.
                    subprocess.run(["python", "main.py"], shell=(os.name == 'nt'))
            except KeyboardInterrupt:
                console.print("\\n  [yellow]>[/yellow] Server stopped by user.")
            except Exception as e:
                console.print(f"  [red]x[/red] Error starting server: {e}")
"""
    
    # We need to find where to insert. The best place is after the final summary Panel.
    # The final summary ends around line 1084.
    
    if "auto_start_code" not in content:
        content = content.replace('padding=(1, 2)\n    ))', 'padding=(1, 2)\n    ))\n' + auto_start_code)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_and_upgrade()
