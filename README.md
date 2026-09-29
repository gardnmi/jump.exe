# jump.exe

**A very hard climb through the five stages of accepting agentic coding. Built for Omarchy.**

You are a developer at the bottom of the desktop. The black pill is behind you.
The white pill is somewhere above fifteen windows, five years of doubt, and
an unreasonable number of missed jumps.

<p align="center">
  <img src="docs/story-preview.png" width="640" alt="jump.exe — Tactical Prompting Adventure. A hoodie-wearing developer leaps up a tower of terminal windows toward the white pill." />
</p>

Charge a jump, pick a direction, commit. Climb inside real desktop windows and
leap between them. Hit a wall and bounce back. Miss a ledge and you can fall
through several rooms. Your wallpaper stays visible behind the game.

Denial, Anger, Bargaining, Depression, and Acceptance each have their own desktop
scenes, reactive creatures, environmental story, and music. A caretaker offers
some context at the bottom. A small, ridiculous reward waits at the top.

Inspired by Jump King and Omarchy's Osaka Jade aesthetic. This is an independent
game with its own art and world, and an early playable release.

## Install

Run this in **Omarchy**, as your normal user:

```sh
curl -fsSL https://raw.githubusercontent.com/gardnmi/jump.exe/main/install.sh | bash
jump.exe
```

Or download `install.py` from the [latest release](https://github.com/gardnmi/jump.exe/releases/latest),
inspect it, and run `python install.py`.

The installer downloads a versioned runtime archive, verifies its SHA-256
checksum and file manifest, and installs into your user directory. It uses
`omarchy pkg add` only if system dependencies are missing. No pip environment,
source build, Git checkout, or changes to your Hyprland configuration are required.
A **jump.exe** entry is added to the application launcher.

Requires a current Omarchy installation with the Hyprland Lua window API, GTK3,
GTK4 layer shell, Python/Cairo, and GStreamer. The game is Linux/Omarchy-only;
`.exe` is part of the name. Start it on the workspace and monitor you want to play on.

## Controls

| Key | Action |
| --- | --- |
| A / D or Left / Right | Walk; choose direction when releasing a jump |
| Hold Space, release | Charge and jump; no steering in the air |
| E | Talk to the caretaker; replay the ending at the summit |
| M | Toggle music mute |
| [ / ] | Lower / raise music volume |
| R | Restart the climb |
| N | Restart with a new seed |
| Esc | Quit |
| F2 | Toggle free-flight practice mode |
| WASD / arrows in practice | Fly; Shift makes it faster |
| Page Up / Page Down in practice | Move between rooms |
| F3 | Retry the saved practice position |

The camera follows you continuously up and down. Switching workspaces or focusing
another application pauses play. Practice runs are marked in the ending results.

```sh
jump.exe --dev --seed 42    # Explore or practice a particular course
jump.exe --mute            # Start with music muted
jump.exe --check           # Diagnose dependencies, assets, and the session
```

## Updates

```sh
jump.exe --version
jump.exe --update
jump.exe --rollback
jump.exe --uninstall
```

An update is unpacked and checked before the `current` release switches. A failed
download or validation leaves the installed game intact. The previous version is
retained for rollback, and an already running game keeps using its own files.
Updates take effect on the next launch. Quit the game before uninstalling.

Default paths are `~/.local/bin/jump.exe`,
`~/.local/share/jump-exe/releases/<version>`, and
`~/.local/share/applications/jump-exe.desktop`. `XDG_DATA_HOME` is respected.

For a pinned or offline install, download the installer, archive, and `SHA256SUMS`
from the same release:

```sh
python install.py --version 0.1.0
python install.py --archive jump.exe-0.1.0-omarchy.tar.gz
```

## Develop

```sh
git clone https://github.com/gardnmi/jump.exe.git
cd jump.exe
./jump.exe --check
./jump.exe --dev
python tools/test.py
python tools/build_release.py
```

Install the documented dependencies first if working directly from source:

```sh
omarchy pkg add python python-gobject python-cairo gtk3 gtk4 gtk4-layer-shell \
  gstreamer gst-plugins-base gst-plugins-good ttf-cascadia-mono-nerd
```

Tests cover the complete physics route, unintended shortcuts, fall paths, pixel
scaling, encounters, ending input, real audio decoding, and install/update/rollback.
They run without opening desktop windows or an audio device.

[Contributing](CONTRIBUTING.md) · [Release process](docs/RELEASING.md) ·
[Level design](docs/DESIGN.md) · [Story](docs/STORY.md) · [Art direction](docs/STYLE.md) ·
[Gameplay art preview](docs/stage-preview.png) ·
[Ending preview — spoilers](docs/ending-preview.mp4)

Code is [MIT licensed](LICENSE). See the separate [asset terms](assets/LICENSE.md)
and [asset provenance](assets/PROVENANCE.md) for artwork and music.
