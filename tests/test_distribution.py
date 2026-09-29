"""Exercise complete release installs in isolated directories, never the real desktop."""
from contextlib import redirect_stdout
from io import BytesIO, StringIO
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import install
from tools.build_release import build
from jump_exe.doctor import check

ROOT = Path(__file__).resolve().parents[1]


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='jump-exe-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = install.locations(self.root/'a prefix with spaces')
        self.data = Path(self.config['data'])
        self.enterContext(redirect_stdout(StringIO()))

    def release(self, number):
        source = self.root/('release-'+number)
        install.stage(ROOT, source)
        (source/'version.txt').write_text(number+'\n')
        manifest = json.loads((source/'MANIFEST.json').read_text())
        manifest['version.txt'] = install.digest(source/'version.txt')
        (source/'MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True))
        return source

    def run_installed(self, *args):
        return subprocess.check_output([self.config['bin'], *args], text=True).strip()

    def test_install_update_rollback_and_uninstall_using_real_launcher(self):
        first, second = self.release('0.1.0'), self.release('0.2.0')
        install.install(first, self.config)
        self.assertEqual(self.run_installed('--version'), 'jump.exe 0.1.0')
        self.assertTrue(Path(self.config['desktop']).is_file())
        if shutil.which('desktop-file-validate'):
            subprocess.run(['desktop-file-validate', self.config['desktop']], check=True)
        # A packaged updater runs from its own release root after this switch.
        install.install(second, self.config)
        self.assertEqual(self.run_installed('--version'), 'jump.exe 0.2.0')
        self.assertIn('0.1.0', self.run_installed('--rollback'))
        self.assertEqual(self.run_installed('--version'), 'jump.exe 0.1.0')
        self.assertEqual((self.data/'releases/0.2.0/version.txt').read_text(), '0.2.0\n')
        self.run_installed('--uninstall')
        self.assertFalse(self.data.exists())
        self.assertFalse(Path(self.config['bin']).exists())
        self.assertFalse(Path(self.config['desktop']).exists())

    def test_bad_update_and_failed_dependency_probe_leave_current_unchanged(self):
        install.install(self.release('0.1.0'), self.config)
        second = self.release('0.2.0')
        original = (second/'launch.py').read_bytes()
        (second/'launch.py').write_text('corrupt')
        with self.assertRaises(ValueError):
            install.install(second, self.config)
        (second/'launch.py').write_bytes(original)
        with patch('install.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'probe')):
            with self.assertRaises(subprocess.CalledProcessError):
                install.install(second, self.config)
        self.assertEqual(self.run_installed('--version'), 'jump.exe 0.1.0')
        self.assertFalse((self.data/'releases/0.2.0').exists())

    def test_idempotent_install_rejects_changed_bytes_under_same_version(self):
        source = self.release('0.1.0')
        install.install(source, self.config, skip_checks=True)
        install.install(source, self.config, skip_checks=True)
        (source/'README.md').write_text('different build')
        manifest = json.loads((source/'MANIFEST.json').read_text())
        manifest['README.md'] = install.digest(source/'README.md')
        (source/'MANIFEST.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(RuntimeError, 'different content'):
            install.install(source, self.config, skip_checks=True)
        self.assertEqual(self.run_installed('--version'), 'jump.exe 0.1.0')

    def test_runtime_archive_is_reproducible_self_contained_and_checksums_work(self):
        a = build(ROOT, self.root/'build-a')
        b = build(ROOT, self.root/'build-b')
        self.assertEqual(install.digest(a), install.digest(b))
        extracted = install.unpack(a, a.parent/'SHA256SUMS', self.root/'extracted')
        with tarfile.open(a) as archive:
            names = archive.getnames()
        self.assertFalse(any('/tests/' in n or '/docs/' in n or '/render_' in n for n in names))
        self.assertFalse(any('king_jump' in n or 'grief-worlds' in n for n in names))
        install.install(extracted, self.config)
        # Installed tree has no dependency on the source checkout or current cwd.
        result = subprocess.check_output([self.config['bin'], '--version'], cwd='/', text=True)
        self.assertEqual(result.strip(), 'jump.exe '+(ROOT/'version.txt').read_text().strip())
        with a.open('ab') as out:
            out.write(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            install.unpack(a, a.parent/'SHA256SUMS', self.root/'invalid')

    def test_rejects_archive_path_traversal_links_and_duplicate_entries(self):
        for mode in ('parent', 'symlink', 'duplicate'):
            with self.subTest(mode=mode):
                archive = self.root/(mode+'.tar.gz')
                with tarfile.open(archive, 'w:gz') as tar:
                    info = tarfile.TarInfo('../outside' if mode=='parent' else 'game/file')
                    info.size = 1
                    if mode == 'symlink':
                        info.type = tarfile.SYMTYPE
                        info.linkname = '/tmp'
                        info.size = 0
                    tar.addfile(info, BytesIO(b'x'))
                    if mode == 'duplicate':
                        tar.addfile(info, BytesIO(b'y'))
                checksum = self.root/'SHA256SUMS'
                checksum.write_text(f'{install.digest(archive)}  {archive.name}\n')
                with self.assertRaisesRegex(ValueError, 'Unsafe'):
                    install.unpack(archive, checksum, self.root/'unsafe')
        self.assertFalse((self.root/'outside').exists())

    def test_offline_install_cli_and_version_without_graphical_imports(self):
        archive = build(ROOT, self.root/'dist')
        subprocess.run([sys.executable, '-I', str(ROOT/'install.py'), '--archive', str(archive),
                        '--prefix', str(self.root/'offline'), '--skip-dependencies'], check=True,
                       stdout=subprocess.DEVNULL)
        result = subprocess.check_output([sys.executable, '-S', str(ROOT/'launch.py'), '--version'], text=True)
        self.assertTrue(result.startswith('jump.exe '))

    def test_bundled_runtime_dependencies_and_assets(self):
        self.assertEqual(check(session=False), [])

    def test_existing_unmanaged_launcher_is_preserved(self):
        launcher = Path(self.config['bin'])
        launcher.parent.mkdir(parents=True)
        launcher.write_text('user file')
        with self.assertRaisesRegex(RuntimeError, 'unmanaged'):
            install.install(self.release('0.1.0'), self.config, skip_checks=True)
        self.assertEqual(launcher.read_text(), 'user file')


if __name__ == '__main__':
    unittest.main()
