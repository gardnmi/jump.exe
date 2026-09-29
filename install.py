#!/usr/bin/python
"""User-local jump.exe installer/updater. Standard library only; no pip or root install."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from urllib.request import Request, urlopen

REPO = 'gardnmi/jump.exe'
PACKAGES = ('python', 'python-gobject', 'python-cairo', 'gtk3', 'gtk4',
            'gtk4-layer-shell', 'gstreamer', 'gst-plugins-base', 'gst-plugins-good',
            'ttf-cascadia-mono-nerd')
MODULES = ('__init__', 'resources', 'cli', 'doctor', 'hyprland', 'main', 'overlay',
           'art', 'atmosphere', 'atmosphere_art', 'character', 'course', 'critters', 'desktop_style', 'devmode',
           'ending', 'environment', 'finale_art', 'landmarks', 'life', 'model',
           'music', 'physics_profile', 'sound', 'stage_scenes', 'story',
           'summit_animation', 'terrain', 'world_details')
ASSETS = ('omarchy-developers.png', 'silent-pixel-realm.opus', 'warning-signal.opus',
          'searching-for-a-signal.opus', 'desolate-arpeggios.opus', 'trionfo-sereno.opus',
          'sfx/jump.wav', 'sfx/land.wav', 'sfx/heavy_land.wav', 'sfx/white_pill.wav')
RUNTIME = ('launch.py', 'jump.exe', 'install.py', 'version.txt', 'LICENSE',
           'README.md', 'assets/PROVENANCE.md', 'assets/LICENSE.md', 'packaging/jump-exe.svg',
           *(f'src/jump_exe/{name}.py' for name in MODULES), *(f'assets/{name}' for name in ASSETS))


def version(text):
    text = text.strip().removeprefix('v')
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', text):
        raise ValueError(f'Invalid release version: {text!r}')
    return text


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def stage(source, target):
    """Explicit runtime allowlist shared by source installs and the release builder."""
    target.mkdir(parents=True, exist_ok=True)
    for name in RUNTIME:
        src, dest = source/name, target/name
        if not src.is_file() or src.is_symlink():
            raise ValueError(f'Missing or invalid runtime file: {src}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        dest.chmod(0o755 if name == 'jump.exe' else 0o644)
    manifest = {name: digest(target/name) for name in RUNTIME}
    (target/'MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')


def verify(root):
    version((root/'version.txt').read_text())
    manifest = json.loads((root/'MANIFEST.json').read_text())
    # Accept future runtime additions, but always require the entry points.
    for name in ('launch.py', 'install.py', 'version.txt', 'src/jump_exe/cli.py'):
        if name not in manifest:
            raise ValueError(f'Release is missing {name}')
    for name, expected in manifest.items():
        file = root/name
        if Path(name).is_absolute() or '..' in Path(name).parts or file.is_symlink():
            raise ValueError('Unsafe release manifest')
        if not file.is_file() or digest(file) != expected:
            raise ValueError(f'Release file failed verification: {name}')


def unpack(archive, checksum, destination):
    # SHA256SUMS binds both the bytes and filename. No unchecked archive option.
    entries = {}
    for line in checksum.read_text().splitlines():
        parts = line.split()
        if len(parts) == 2 and re.fullmatch('[0-9a-fA-F]{64}', parts[0]):
            entries[parts[1].lstrip('*')] = parts[0].lower()
    if entries.get(archive.name) != digest(archive):
        raise ValueError('Archive checksum mismatch; current installation was not changed.')
    with tarfile.open(archive, 'r:gz') as bundle:
        members = bundle.getmembers()
        if not members or sum(m.size for m in members) > 256*1024*1024:
            raise ValueError('Empty or oversized release archive')
        seen = set()
        for member in members:
            path = Path(member.name)
            if (path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir())
                    or member.name in seen):
                raise ValueError('Unsafe release archive entry')
            seen.add(member.name)
        roots = {Path(m.name).parts[0] for m in members}
        if len(roots) != 1:
            raise ValueError('Expected one release directory')
        bundle.extractall(destination, filter='data')
    root = destination/roots.pop()
    verify(root)
    return root


def fetch(url, path):
    with urlopen(Request(url, headers={'User-Agent': 'jump.exe-installer'}), timeout=60) as response:
        with path.open('wb') as out:
            shutil.copyfileobj(response, out)


def download(target, requested=None):
    if requested:
        tag = 'v'+version(requested)
    else:
        # Resolve latest once; all assets come from this exact immutable tag URL.
        with urlopen(Request(f'https://api.github.com/repos/{REPO}/releases/latest',
                             headers={'User-Agent': 'jump.exe-installer'}), timeout=30) as response:
            tag = 'v'+version(json.load(response)['tag_name'])
    base = f'https://github.com/{REPO}/releases/download/{tag}'
    archive = target/f'jump.exe-{version(tag)}-omarchy.tar.gz'
    checksum = target/'SHA256SUMS'
    print(f'Downloading jump.exe {tag}...', flush=True)
    fetch(base+'/'+archive.name, archive)
    fetch(base+'/SHA256SUMS', checksum)
    root = unpack(archive, checksum, target/'unpacked')
    if (root/'version.txt').read_text().strip() != version(tag):
        raise ValueError('Downloaded release version does not match the requested tag')
    return root


def dependencies():
    if not shutil.which('omarchy') or not shutil.which('pacman'):
        raise RuntimeError('jump.exe supports Omarchy only.')
    result = subprocess.run(['pacman', '-T', *PACKAGES], text=True, capture_output=True)
    if result.returncode not in (0, 127):
        raise RuntimeError(result.stderr.strip() or 'Unable to check Omarchy packages')
    missing = result.stdout.split()
    if missing:
        print('Installing required Omarchy packages: '+' '.join(missing), flush=True)
        subprocess.run(['omarchy', 'pkg', 'add', *missing], check=True)


def locations(prefix=None):
    if prefix:
        prefix = Path(prefix).expanduser().resolve()
        data, binaries = prefix/'share', prefix/'bin'
    else:
        data = Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share')).expanduser().resolve()
        binaries = Path.home()/'.local/bin'
    return {'data': str(data/'jump-exe'), 'bin': str(binaries/'jump.exe'),
            'desktop': str(data/'applications/jump-exe.desktop')}


def installed_config():
    source = Path(__file__).resolve()
    data = source.parent.parent.parent
    config = data/'install.json'
    if source.parent.parent.name != 'releases' or not config.is_file():
        raise RuntimeError('This is a source checkout. Install with: python install.py --source .')
    result = json.loads(config.read_text())
    if Path(result['data']).resolve() != data:
        raise ValueError('Invalid installation record')
    return result


@contextmanager
def locked(data):
    data.mkdir(parents=True, exist_ok=True)
    with (data/'.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another jump.exe install/update is running.') from None
        yield


def atomic_text(path, text, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        temp = Path(tmp.name)
        tmp.write(text.encode())
    try:
        temp.chmod(mode)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def point(link, target):
    temp = link.with_name(link.name+'.new')
    temp.unlink(missing_ok=True)
    temp.symlink_to(target)
    temp.replace(link)


def desktop_quote(value):
    # Desktop Exec has its own quoting, distinct from a shell command.
    value = str(value).replace('%', '%%').replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
    return '"'+value+'"'


def install(source, config, skip_checks=False):
    verify(source)
    number = version((source/'version.txt').read_text())
    data = Path(config['data'])
    with locked(data):
        marker = data/'install.json'
        if marker.exists() and json.loads(marker.read_text()) != config:
            raise RuntimeError('Installation paths changed. Uninstall the existing copy first.')
        for path in (Path(config['bin']), Path(config['desktop'])):
            if path.exists() and not marker.exists():
                raise RuntimeError(f'Refusing to replace an unmanaged file: {path}')
        releases = data/'releases'
        releases.mkdir(exist_ok=True)
        dest = releases/number
        with tempfile.TemporaryDirectory(dir=releases, prefix='.staging-') as temp:
            candidate = Path(temp)/number
            shutil.copytree(source, candidate)
            verify(candidate)
            if not skip_checks:
                code = "import sys; sys.path.insert(0,sys.argv[1]); from jump_exe.doctor import check; errors=check(session=False); print('\\n'.join(errors)); sys.exit(bool(errors))"
                subprocess.run([sys.executable, '-I', '-c', code, str(candidate/'src')], check=True)
            if dest.exists():
                verify(dest)
                if (dest/'MANIFEST.json').read_bytes() != (candidate/'MANIFEST.json').read_bytes():
                    raise RuntimeError(f'Version {number} is already installed with different content.')
            else:
                candidate.rename(dest)
        current = data/'current'
        old = os.readlink(current) if current.is_symlink() else None
        launcher = '#!/usr/bin/env bash\nexec /usr/bin/python -I '+shlex.quote(str(current/'launch.py'))+' "$@"\n'
        desktop = ('[Desktop Entry]\nType=Application\nName=jump.exe\n'
                   'Comment=Climb through the five stages of accepting agentic coding\n'
                   f'Exec={desktop_quote(config["bin"])}\n'
                   f'Icon={current}/packaging/jump-exe.svg\n'
                   'Terminal=false\nCategories=Game;ActionGame;\nStartupNotify=false\n')
        atomic_text(Path(config['bin']), launcher, 0o755)
        atomic_text(Path(config['desktop']), desktop)
        atomic_text(marker, json.dumps(config, indent=2)+'\n')
        relative = 'releases/'+number
        if old and old != relative:
            point(data/'previous', old)
        point(current, relative)
        # Old releases are intentionally retained: running games still load assets from them.
    print(f'Installed jump.exe {number}. Launch: {config["bin"]}')


def rollback(config, skip_checks=False):
    data = Path(config['data'])
    with locked(data):
        previous, current = data/'previous', data/'current'
        if not previous.is_symlink():
            raise RuntimeError('No previous release to roll back to.')
        target = previous.resolve()
        if target.parent != (data/'releases').resolve():
            raise RuntimeError('Invalid rollback target')
        verify(target)
        old, back = os.readlink(current), os.readlink(previous)
        point(current, back)
        point(previous, old)
        print(f'Now using jump.exe {(target/"version.txt").read_text().strip()}')


def uninstall(config):
    data = Path(config['data'])
    with locked(data):
        if json.loads((data/'install.json').read_text()) != config:
            raise RuntimeError('Invalid installation record')
        for key in ('bin', 'desktop'):
            Path(config[key]).unlink(missing_ok=True)
        for name in ('current', 'previous', 'install.json'):
            (data/name).unlink(missing_ok=True)
        shutil.rmtree(data/'releases')
    (data/'.lock').unlink()
    data.rmdir()
    print('jump.exe uninstalled.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--source', type=Path, help='Install a source checkout')
    mode.add_argument('--archive', type=Path, help='Install a downloaded runtime archive')
    mode.add_argument('--update', action='store_true')
    mode.add_argument('--rollback', action='store_true')
    mode.add_argument('--uninstall', action='store_true')
    parser.add_argument('--checksum', type=Path, help='SHA256SUMS beside the archive by default')
    parser.add_argument('--version', help='Pin a release, for example 0.1.0')
    parser.add_argument('--prefix', type=Path, help='Alternate user install prefix')
    parser.add_argument('--skip-dependencies', action='store_true', help='Packaging tests only: skip system checks')
    args = parser.parse_args()
    if os.geteuid() == 0 and not args.skip_dependencies:
        parser.error('Run as your normal user. Only missing system packages need elevation.')
    if args.skip_dependencies and not args.prefix and not (args.update or args.rollback or args.uninstall):
        parser.error('--skip-dependencies requires an isolated --prefix')
    try:
        config = installed_config() if args.update or args.rollback or args.uninstall else locations(args.prefix)
        if args.rollback:
            rollback(config)
            return 0
        if args.uninstall:
            uninstall(config)
            return 0
        if not args.skip_dependencies:
            dependencies()
        with tempfile.TemporaryDirectory(prefix='jump-exe-download-') as temp:
            temp = Path(temp)
            if args.source:
                source = temp/'source'
                stage(args.source.resolve(), source)
            elif args.archive:
                source = unpack(args.archive, args.checksum or args.archive.parent/'SHA256SUMS', temp/'unpacked')
            else:
                source = download(temp, args.version)
            install(source, config, skip_checks=args.skip_dependencies)
        return 0
    except (OSError, ValueError, RuntimeError, KeyError, tarfile.TarError, subprocess.CalledProcessError) as error:
        print(f'jump.exe install: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
