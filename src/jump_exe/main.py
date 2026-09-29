#!/usr/bin/env python3
"""jump.exe: charged jumps through a living Omarchy desktop."""
import argparse
import json
import cairo
import os
from pathlib import Path
import signal
import secrets
import subprocess
import sys
import tempfile
import time

from .resources import ROOT
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLibUnix', '2.0')
from gi.repository import Gtk, Gdk, GLib, GLibUnix
from .hyprland import Hyprland
from .model import King, ledges, Tower, Camera, window_for
from .art import tile
from .devmode import DevMode
from .story import Story
from .music import Music
from .sound import SoundEffects
from .course import SUMMIT
from .ending import focus_summit



class App:
    def __init__(self, state_file=None, seed=None, dev=False, muted=False):
        self.closed = False
        self.error = None
        self.windows, self.clients, self.rectangles = {}, {}, {}
        self.timers = []
        self.helper = self.temp = self.rule = None
        self.visible = self.ready = False
        self.keys = set()
        self.level = 0
        self.seed = seed if seed is not None else secrets.randbits(32)
        self.assignments = {}
        self.sent = {}
        self.views = {}
        self.accepted = False
        self.dev = DevMode(dev)
        self.story = Story()
        self.music = Music(muted)
        self.sounds = SoundEffects()
        self.state_file = state_file
        self.hypr = Hyprland()
        try:
            self.setup()
        except BaseException:
            self.close()
            raise

    def setup(self):
        workspace = self.hypr.request('activeworkspace', True)
        self.workspace = workspace['id']
        workspace_selector = str(self.workspace) if self.workspace > 0 else 'name:'+workspace['name']
        monitor = next(m for m in self.hypr.request('monitors', True) if m['focused'])
        self.bounds = (monitor['x'], monitor['y'], monitor['width']/monitor['scale'], monitor['height']/monitor['scale'])
        self.king = King(*self.bounds[2:])
        self.tower = Tower(self.bounds,self.seed)
        self.camera = Camera(self.bounds)
        self.platforms = ledges(self.tower.near(self.tower.base))
        self.king.enter(self.platforms)
        self.sounds.sync(self.king)
        if self.dev.active:
            self.dev.enter(self.king)
        self.prefix = f'JumpExe-{os.getpid()}'
        self.rule = f'jump_exe_{os.getpid()}'
        self.hypr.request(f'eval {self.rule}=hl.window_rule({{name="{self.rule}",match={{initial_title="^{self.prefix}-.*$"}},workspace={json.dumps(workspace_selector)},float=true,no_anim=true,rounding=0,border_size=0,no_shadow=true,no_blur=true,opacity="1 override 1 override"}})')
        self.temp = tempfile.TemporaryDirectory(prefix='jump-exe-')
        self.ipc = Path(self.temp.name)/'state.json'
        self.publish()
        self.helper = subprocess.Popen([sys.executable,'-I',str(ROOT/'launch.py'),'--overlay',str(self.ipc),str(os.getpid()),monitor['name']],env={**os.environ,'GDK_BACKEND':'wayland'})
        for slot in range(12):
            self.add(str(slot))
        self.started = self.last = time.monotonic()
        self.timers.append(GLib.timeout_add(60,lambda: self.guard(self.sync)))
        self.timers.append(GLib.timeout_add(16,lambda: self.guard(self.tick)))
        for sig in (signal.SIGTERM, signal.SIGINT):
            self.timers.append(GLibUnix.signal_add(GLib.PRIORITY_DEFAULT,sig,self.close))

    def guard(self, callback):
        try:
            return callback()
        except Exception as error:
            self.error = str(error)
            print(f'jump.exe: {error}',file=sys.stderr,flush=True)
            self.close()
            return False

    def add(self, role):
        win = Gtk.Window(title=f'{self.prefix}-{role}')
        win.set_decorated(False)
        win.set_default_size(300,80)
        win.set_focus_on_map(False)
        win.set_app_paintable(True)
        visual = win.get_screen().get_rgba_visual()
        if visual:
            win.set_visual(visual)
        win.set_opacity(0.)
        win.connect('realize',lambda widget: widget.get_window().input_shape_combine_region(cairo.Region(),0,0))
        win.connect('delete-event',lambda *_: self.close() or True)
        win.connect('key-press-event',self.key,True)
        win.connect('key-release-event',self.key,False)
        area = Gtk.DrawingArea()
        area.connect('draw',self.draw,role)
        win.add(area)
        self.windows[role] = win
        win.show_all()

    def sync(self):
        if self.closed:
            return False
        if self.helper.poll() is not None:
            raise RuntimeError('Character overlay exited; GTK4 layer-shell is required.')
        clients = self.hypr.request('clients',True)
        self.clients = {role: next((c for c in clients if c.get('initialTitle') == f'{self.prefix}-{role}'),None) for role in self.windows}
        workspace = self.hypr.request('activeworkspace',True)['id']
        active = self.hypr.request('activewindow',True).get('address')
        self.visible = workspace == self.workspace and all(
            c is not None and c['workspace']['id']==self.workspace for c in self.clients.values())
        self.focused = active in {c['address'] for c in self.clients.values() if c}
        if not self.visible or not self.focused:
            self.keys.clear()
            self.king.cancel()
        if any(c is None for c in self.clients.values()):
            if self.ready or time.monotonic()-self.started > 15:
                raise RuntimeError('A platform window disappeared or failed to map.')
            return True
        if not self.ready:
            self.ready = True
            self.place_windows()
            if workspace == self.workspace:
                room = window_for(self.king.room) or str(self.dev.room_index(self.king,self.tower))
                slot = next(s for s,r in self.assignments.items() if r == room)
                self.hypr.focus(self.clients[slot]['address'])
                self.focused = True
            print(f'READY workspace={self.workspace} seed={self.seed} continuous tower',flush=True)
        return True

    def place_windows(self):
        # Reuse a fixed pool: offscreen surfaces are transparent and click-through.
        # No window creation/focus changes interrupt a held jump during scrolling.
        self.views = self.tower.view(self.camera.offset)
        for slot,role in list(self.assignments.items()):
            if role not in self.views:
                self.windows[slot].set_opacity(0.)
                self.windows[slot].get_window().input_shape_combine_region(cairo.Region(),0,0)
                del self.assignments[slot]
                self.sent.pop(slot,None)
        for role in self.views:
            if role not in self.assignments.values():
                slot = next(s for s in self.windows if s not in self.assignments)
                self.assignments[slot] = role
        actions = []
        for slot,role in self.assignments.items():
            rect,clip,full_height = self.views[role]
            x,y,w,h = rect
            previous = self.sent.get(slot)
            selector = json.dumps('address:'+self.clients[slot]['address'])
            if previous != rect:
                if previous is None or previous[2:] != rect[2:]:
                    actions.append(f'hl.dsp.window.resize({{window={selector},x={w},y={h}}})')
                actions.append(f'hl.dsp.window.move({{window={selector},x={x},y={y}}})')
                self.sent[slot] = rect
        if actions:
            self.hypr.run(*actions)
        for slot in self.assignments:
            self.windows[slot].set_opacity(1.)
            self.windows[slot].get_window().input_shape_combine_region(
                cairo.Region(cairo.RectangleInt(0,0,self.sent[slot][2],self.sent[slot][3])),0,0)
            self.windows[slot].queue_draw()
        self.rectangles = {role:view[0] for role,view in self.views.items()}

    def direction(self):
        return int(bool(self.keys & {'d','right'}))-int(bool(self.keys & {'a','left'}))

    def key(self, win, event, pressed):
        key = Gdk.keyval_name(event.keyval).lower()
        if pressed and key in self.keys:
            return True
        if pressed:
            self.keys.add(key)
        else:
            self.keys.discard(key)
        if key == 'escape' and pressed:
            self.close()
        elif self.ready:
            if key == 'm' and pressed:
                self.music.toggle_mute()
            elif key in ('bracketleft','bracketright') and pressed:
                self.music.adjust_volume(key=='bracketright')
            elif self.story.ending.active:
                action=self.story.ending.command(key) if pressed else None
                if action=='new_seed':
                    self.seed=secrets.randbits(32)
                if action in ('restart','new_seed'):
                    self.restart()
                elif action=='dismiss':
                    self.king.cancel()
                    self.keys.clear()
            elif key == 'f2' and pressed:
                if self.dev.active:
                    self.dev.resume(self.king,self.platforms)
                else:
                    self.dev.enter(self.king)
                self.sounds.sync(self.king)
            elif key == 'f3' and pressed:
                if self.dev.retry(self.king,self.platforms):
                    self.recenter()
                    self.sounds.sync(self.king)
            elif self.dev.active and pressed and key in {'page_up','page_down','prior','next'}:
                direction = 1 if key in {'page_up','prior'} else -1
                if self.dev.skip_room(self.king,self.platforms,self.tower,direction):
                    self.recenter()
            elif key == 'r' and pressed:
                self.restart()
            elif key == 'n' and pressed:
                self.seed = secrets.randbits(32)
                self.restart()
            elif key == 'e' and pressed and not self.dev.active:
                if self.story.accepted and self.king.room==SUMMIT:
                    self.story.replay_ending(self.king,self.tower)
                    self.king.cancel()
                    self.sounds.celebrate(self.music.muted)
                else:
                    self.story.talk()
            elif key == 'space' and not self.dev.active:
                if pressed:
                    self.king.press()
                else:
                    self.king.release(self.direction())
        return True

    def tick(self):
        if self.closed:
            return False
        now = time.monotonic()
        dt = min(.05,now-self.last)
        self.last = now
        if self.ready and self.visible:
            if self.focused:
                self.platforms = ledges(self.tower.near(self.king.y))
                if self.story.ending.active:
                    self.king.cancel()
                elif self.dev.active:
                    self.dev.move(self.king,dt,self.keys,self.tower)
                else:
                    self.king.step(dt,self.platforms,self.direction(),self.bounds)
                if self.story.ending.active:
                    focus_summit(self.camera,self.tower,dt)
                else:
                    self.camera.step(dt,self.king.y)
                was_accepted=self.story.accepted
                self.story.update(dt,self.king,self.tower,self.dev.active)
                if self.story.accepted and not was_accepted:
                    self.king.cancel()
                    self.keys.clear()
                    self.sounds.celebrate(self.music.muted)
                self.level = (self.dev.room_index(self.king,self.tower)//3 if self.dev.active else
                              int(window_for(self.king.room))//3 if self.king.room else
                              self.tower.level_at(self.king.y))
                self.accepted = self.story.accepted
            self.place_windows()
        self.music.update(dt,self.level,self.ready and self.visible and getattr(self,'focused',False))
        self.sounds.clips['complete'].set_mute(self.music.muted)
        self.sounds.update(self.king,self.ready and self.visible and getattr(self,'focused',False)
                           and not self.dev.active)
        self.publish()
        return True

    def restart(self):
        self.tower = Tower(self.bounds,self.seed)
        self.camera = Camera(self.bounds)
        self.platforms = ledges(self.tower.near(self.tower.base))
        self.king.reset(self.platforms)
        self.sounds.sync(self.king)
        self.dev = DevMode(self.dev.active)
        self.story = Story()
        if self.dev.active:
            self.dev.enter(self.king)
        self.keys.clear()
        self.level = 0
        self.accepted = False

    def recenter(self):
        self.camera.offset = min(0.,self.king.y-self.bounds[1]-self.bounds[3]*.55)

    def publish(self):
        data = dict(visible=self.visible and self.ready,stamp=time.monotonic(),origin=self.bounds[:2],
                    x=self.king.x,y=self.king.y-self.camera.offset,facing=self.king.facing,charge=self.king.charge,
                    level=self.level,camera=self.camera.offset,world_y=self.king.y,
                    phase=self.king.walk_phase if self.king.walking else self.story.time,
                    sprite_scale=self.king.scale,pose='idle' if self.dev.active else self.king.pose,impact=self.king.impact,
                    dev_mode=self.dev.active,practice_ready=self.dev.checkpoint is not None,
                    dev_blocked=self.dev.active and not self.dev.clear_at(self.king,self.platforms),
                    dev_room=self.dev.room_index(self.king,self.tower),
                    accepted=self.accepted,focused=getattr(self,'focused',False),
                    music_muted=self.music.muted,music_available=self.music.available,
                    music_volume=self.music.volume,
                    music_mix=[round(gain,4) for gain in self.music.weights],
                    trail=[(x,y-self.camera.offset) for x,y in self.king.trail],
                    room=window_for(self.king.room),platform=self.king.room,jumps=self.king.jumps,
                    falls=self.king.falls,workspace=self.workspace,rectangles=self.rectangles)
        data.update(self.story.state(self.camera.offset))
        for path in (getattr(self,'ipc',None),self.state_file):
            if path:
                tmp = path.with_suffix('.tmp')
                tmp.write_text(json.dumps(data))
                tmp.replace(path)

    def draw(self, area, c, slot):
        c.set_operator(cairo.OPERATOR_SOURCE)
        c.set_source_rgba(0,0,0,0)
        c.paint()
        c.set_operator(cairo.OPERATOR_OVER)
        role = self.assignments.get(slot)
        if role in self.views:
            rect,clip,full_height = self.views[role]
            c.translate(0,-clip)
            tile(c,rect[2],full_height,int(role),int(role)//3,self.story.time,
                 self.accepted,self.story.guide_near and self.story.page<4,
                 events=self.story.life.room(int(role)),ending=self.story.ending.state())

    def close(self, *_):
        if self.closed:
            return False
        self.closed = True
        self.music.close()
        self.sounds.close()
        for timer in self.timers:
            GLib.source_remove(timer)
        self.timers.clear()
        if self.helper:
            if self.helper.poll() is None:
                self.helper.terminate()
            try:
                self.helper.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.helper.kill()
                self.helper.wait()
        for window in self.windows.values():
            window.destroy()
        if self.rule:
            try:
                self.hypr.request(f'eval if {self.rule} then {self.rule}:set_enabled(false); {self.rule}=nil end')
            except Exception as error:
                print(f'Rule cleanup: {error}',file=sys.stderr)
        if self.temp:
            self.temp.cleanup()
        if Gtk.main_level():
            Gtk.main_quit()
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-file',type=Path,help='Export live state for debugging')
    parser.add_argument('--seed',type=int,help='Repeat a particular random course')
    parser.add_argument('--dev',action='store_true',help='Start in free-flight practice mode (F2 toggles)')
    parser.add_argument('--mute',action='store_true',help='Start with music muted (M toggles)')
    args = parser.parse_args()
    GLib.set_prgname('jump.exe')
    app = App(args.state_file,args.seed,args.dev,args.mute)
    try:
        Gtk.main()
    finally:
        app.close()
    return bool(app.error)


if __name__ == '__main__':
    sys.exit(main())
