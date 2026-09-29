"""GTK4 layer-shell sprite surface, separate from the GTK3 game process."""
from ctypes import CDLL
CDLL('libgtk4-layer-shell.so')
import json
import os
from pathlib import Path
import sys
import time
import gi
import cairo

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gtk, Gdk, GLib, Gtk4LayerShell as Layer
from .art import knight, GOLD, hud
from .desktop_style import WHITE,JADE


class Overlay(Gtk.Application):
    def do_activate(self):
        self.data = {}
        self.window = Gtk.Window(application=self)
        Layer.init_for_window(self.window)
        Layer.set_namespace(self.window, 'jump-exe')
        Layer.set_layer(self.window, Layer.Layer.OVERLAY)
        Layer.set_keyboard_mode(self.window, Layer.KeyboardMode.NONE)
        Layer.set_exclusive_zone(self.window, -1)
        monitors = Gdk.Display.get_default().get_monitors()
        for i in range(monitors.get_n_items()):
            monitor = monitors.get_item(i)
            if monitor.get_connector() == sys.argv[3]:
                Layer.set_monitor(self.window, monitor)
                break
        for edge in (Layer.Edge.TOP, Layer.Edge.BOTTOM, Layer.Edge.LEFT, Layer.Edge.RIGHT):
            Layer.set_anchor(self.window, edge, True)
        css = Gtk.CssProvider()
        css.load_from_data(b'window, drawingarea { background: transparent; }')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.window.connect('realize', lambda win: win.get_surface().set_input_region(cairo.Region()))
        self.area = Gtk.DrawingArea()
        self.area.set_draw_func(self.draw)
        self.window.set_child(self.area)
        GLib.timeout_add(16, self.tick)

    def tick(self):
        if os.getppid() != int(sys.argv[2]):
            self.quit()
            return False
        try:
            self.data = json.loads(Path(sys.argv[1]).read_text())
        except (OSError, ValueError):
            return True
        visible = self.data.get('visible', False) and time.monotonic()-self.data.get('stamp', 0) < 1
        self.window.set_visible(visible)
        if visible:
            self.area.queue_draw()
        return True

    def draw(self, area, c, w, h):
        d = self.data
        if not d.get('visible'):
            return
        if d.get('ending',{}).get('active'):
            hud(c,w,h,d)
            return
        ox, oy = d['origin']
        size = max(1,round(d['sprite_scale']))
        for x,y,life,gold in d.get('particles',[]):
            color = WHITE if gold else JADE
            c.set_source_rgba(*color,min(1,life*3))
            c.rectangle(round(x-ox),round(y-oy),size,size)
            c.fill()
        knight(c,d['x']-ox,d['y']-oy,d['facing'],d['charge'],d.get('phase',0),
               d['sprite_scale'],d['pose'],effects=d.get('avatar_fx'))
        hud(c,w,h,d)


def main():
    return Overlay(application_id=f'io.github.gardnmi.JumpExe{sys.argv[2]}').run([])


if __name__ == '__main__':
    sys.exit(main())
