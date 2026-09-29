#!/usr/bin/python
"""Build a reproducible, self-contained runtime archive and its download checksums."""
import argparse
import gzip
from io import BytesIO
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from install import stage, version, digest, verify


def build(source, output):
    number = version((source/'version.txt').read_text())
    output.mkdir(parents=True, exist_ok=True)
    archive = output/f'jump.exe-{number}-omarchy.tar.gz'
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)/f'jump.exe-{number}'
        stage(source, root)
        verify(root)
        with archive.open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as bundle:
                for path in sorted(root.rglob('*')):
                    if not path.is_file():
                        continue
                    info = tarfile.TarInfo(str(path.relative_to(root.parent)))
                    info.size = path.stat().st_size
                    info.mode = 0o755 if path.name == 'jump.exe' else 0o644
                    info.mtime = info.uid = info.gid = 0
                    bundle.addfile(info, BytesIO(path.read_bytes()))
    installer = output/'install.py'
    shutil.copyfile(source/'install.py', installer)
    (output/'SHA256SUMS').write_text(''.join(f'{digest(file)}  {file.name}\n' for file in (archive, installer)))
    print(f'{archive.name}: {archive.stat().st_size:,} bytes')
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'dist')
    args = parser.parse_args()
    build(ROOT, args.output)
