"""Read-only preflight. GTK3 and GTK4 are checked in separate processes."""
import os
import shutil
import subprocess
import sys
from .resources import ASSETS

PROBES = (
    "import cairo, gi; gi.require_version('Gtk','3.0'); gi.require_version('GLibUnix','2.0'); from gi.repository import Gtk, GLibUnix",
    "from ctypes import CDLL; CDLL('libgtk4-layer-shell.so'); import gi; gi.require_version('Gtk','4.0'); gi.require_version('Gtk4LayerShell','1.0'); from gi.repository import Gtk, Gtk4LayerShell",
    "import gi; gi.require_version('Gst','1.0'); from gi.repository import Gst; Gst.init(None); assert all(Gst.ElementFactory.find(n) for n in ('playbin','opusdec','oggdemux','wavparse','autoaudiosink')), 'Missing GStreamer audio plugins'",
)


def check(verbose=False, session=True):
    errors = []
    if session:
        if not shutil.which('omarchy'):
            errors.append('jump.exe requires Omarchy. Run it from your Omarchy desktop.')
        if not os.environ.get('HYPRLAND_INSTANCE_SIGNATURE') or not os.environ.get('WAYLAND_DISPLAY'):
            errors.append('No active Hyprland/Wayland session. Launch jump.exe inside Omarchy.')
        if not errors:
            try:
                from .hyprland import Hyprland
                hypr = Hyprland()
                hypr.request('eval assert(type(hl.window_rule)=="function" and type(hl.dispatch)=="function", "Lua window API required")')
            except (OSError, RuntimeError, ValueError) as error:
                errors.append(f'Hyprland Lua window API unavailable: {error}. Update Omarchy first.')
    for label, code in zip(('GTK3/Cairo', 'GTK4 layer shell', 'GStreamer audio'), PROBES):
        result = subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, text=True)
        if result.returncode:
            errors.append(f'{label}: {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "unavailable"}')
        elif verbose:
            print(f'OK  {label}')
    from .music import TRACKS
    required = [ASSETS/'omarchy-developers.png', *TRACKS,
                *(ASSETS/'sfx'/name for name in ('jump.wav','land.wav','heavy_land.wav','white_pill.wav'))]
    for path in required:
        if not path.is_file():
            errors.append(f'Missing asset: {path.name}. Reinstall jump.exe.')
    if verbose and not errors:
        print('OK  bundled assets' + (' and Omarchy session' if session else ''))
    if errors:
        errors.append('Dependencies: omarchy pkg add python python-gobject python-cairo gtk3 gtk4 gtk4-layer-shell gstreamer gst-plugins-base gst-plugins-good ttf-cascadia-mono-nerd')
    return errors
