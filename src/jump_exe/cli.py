"""Management commands work without GTK, a compositor, or an audio device."""
import argparse
from pathlib import Path
import subprocess
import sys
from .resources import ROOT


def main():
    if sys.argv[1:2] == ['--overlay']:
        del sys.argv[1]
        from .overlay import main as overlay
        return overlay()
    parser = argparse.ArgumentParser(prog='jump.exe', description='A charged-jump desktop climb for Omarchy.')
    parser.add_argument('--version', action='version', version='jump.exe ' + (ROOT/'version.txt').read_text().strip())
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true', help='Check assets, dependencies, and the Omarchy session')
    actions.add_argument('--update', action='store_true', help='Install the latest published release')
    actions.add_argument('--rollback', action='store_true', help='Switch back to the previous installed release')
    actions.add_argument('--uninstall', action='store_true', help='Remove this user installation')
    parser.add_argument('--state-file', type=Path, help='Export live state for debugging')
    parser.add_argument('--seed', type=int, help='Repeat a particular course')
    parser.add_argument('--dev', action='store_true', help='Start in free-flight practice mode')
    parser.add_argument('--mute', action='store_true', help='Start with music muted')
    args = parser.parse_args()
    for action in ('update', 'rollback', 'uninstall'):
        if getattr(args, action):
            return subprocess.call([sys.executable, '-I', str(ROOT/'install.py'), '--'+action])
    from .doctor import check
    errors = check(verbose=args.check)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    if args.check:
        return 0
    try:
        from .main import main as play
        return play()
    except (OSError, RuntimeError, ValueError, ImportError) as error:
        print(f'jump.exe: {error}', file=sys.stderr)
        return 1
