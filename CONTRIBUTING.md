# Contributing

Use conventional commit messages: `fix:` for a patch, `feat:` for a feature,
and `feat!:` or `fix!:` for a breaking change. Squash PR titles should follow
the same convention. Release Please uses these to prepare the next release PR.

Run `python tools/test.py` before submitting. For visual changes, render and
inspect the affected rooms with `PYTHONPATH=src python -m jump_exe.render_world`.
Keep art on the shared native pixel grid and preserve the solid terrain silhouette.

The game intentionally has difficult jumps and long falls. Layout changes should
be checked with the real physics solver and shortcut auditor, rather than adding
extra platforms that allow players to skip a stage:

```sh
PYTHONPATH=src python -m jump_exe.routecheck --seed 42 --audit
PYTHONPATH=src python -m jump_exe.shortcutcheck --output /tmp/jump-exe-shortcuts.json
```

Gameplay modules live in `src/jump_exe`. GTK3 owns the platform windows; a separate
GTK4 process draws the character overlay. Keep these GTK versions in separate
processes. Assets resolve relative to the loaded release, so changing the installed
`current` symlink cannot affect a game already running.

`install.py` defines the runtime file allowlist. Add new runtime files there.
Never put downloaded game assets, recordings of a personal desktop, secrets,
virtual environments, or generated build output into a release.

See [RELEASING.md](docs/RELEASING.md) for automated publishing and recovery.
