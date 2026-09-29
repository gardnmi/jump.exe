#!/usr/bin/env python3
"""Publish only tested artifacts; reuse an interrupted draft on a workflow rerun."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from install import digest, version


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True).strip()


def main():
    repo = os.environ['GITHUB_REPOSITORY']
    for pr in json.loads(os.environ.get('RELEASE_PRS') or '[]'):
        branch = pr['headBranchName']
        if not branch.startswith('release-please--'):
            raise ValueError('Unexpected release PR branch')
        gh('api', '--method', 'POST', f'repos/{repo}/actions/workflows/ci.yml/dispatches', '-f', f'ref={branch}')
        print(f'CI dispatched for {branch}', flush=True)
    tag = 'v'+version((ROOT/'version.txt').read_text())
    releases = json.loads(gh('api', f'repos/{repo}/releases?per_page=100'))
    release = next((r for r in releases if r['tag_name'] == tag), None)
    if not release or not release['draft']:
        print('No unpublished release for this commit.')
        return
    subprocess.run(['git', 'fetch', 'origin', 'tag', tag], check=True)
    commit = subprocess.check_output(['git', 'rev-parse', tag+'^{commit}'], text=True).strip()
    if commit != os.environ['GITHUB_SHA']:
        raise ValueError('Draft tag is not this tested commit. Re-run the original failed workflow.')
    dist = ROOT/'dist'
    expected = {f'jump.exe-{version(tag)}-omarchy.tar.gz', 'install.py'}
    lines = (dist/'SHA256SUMS').read_text().splitlines()
    recorded = {line.split()[1]: line.split()[0] for line in lines}
    if set(recorded) != expected or any(digest(dist/name) != recorded[name] for name in expected):
        raise ValueError('Release artifact checksum or version mismatch')
    gh('release', 'upload', tag, *(str(dist/name) for name in sorted(expected|{'SHA256SUMS'})), '--clobber')
    gh('release', 'edit', tag, '--draft=false', '--latest')
    print(f'Published https://github.com/{repo}/releases/tag/{tag}')


if __name__ == '__main__':
    main()
