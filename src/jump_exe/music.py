"""Loop and crossfade stage soundtracks on the game's GLib event loop."""
import math
from pathlib import Path
import sys


from .resources import ASSETS
# Denial, Anger, Bargaining, Depression, Acceptance.
TRACKS = (ASSETS/'silent-pixel-realm.opus', ASSETS/'warning-signal.opus',
          ASSETS/'searching-for-a-signal.opus', ASSETS/'desolate-arpeggios.opus',
          ASSETS/'trionfo-sereno.opus')
FADE_SECONDS = 2.
# Half the previous signal amplitude (-6 dB), for a clear background level.
VOLUME = .144


class Song:
    def __init__(self, track, muted=False, audio_sink=None):
        self.muted = muted
        self.active = False
        self.error = None
        self.player = self.bus = self.watch = None
        try:
            if not track.is_file():
                raise FileNotFoundError(f'Soundtrack not found: {track}')
            import gi
            gi.require_version('Gst', '1.0')
            from gi.repository import Gst
            Gst.init(None)
            self.gst = Gst
            self.player = Gst.ElementFactory.make('playbin', None)
            if self.player is None:
                raise RuntimeError('GStreamer playbin is unavailable')
            self.player.set_property('uri', track.resolve().as_uri())
            self.player.set_property('volume', 0.)
            self.player.set_property('mute', self.muted)
            if audio_sink is not None:
                self.player.set_property('audio-sink', audio_sink)
            self.bus = self.player.get_bus()
            self.bus.add_signal_watch()
            self.watch = self.bus.connect('message', self.message)
        except Exception as error:
            self.fail(str(error))

    @property
    def available(self):
        return self.player is not None

    def set_active(self, active):
        """Preserve the playback position while the game is paused or unfocused."""
        if not self.available or self.active == active:
            return
        self.active = active
        state = self.gst.State.PLAYING if active else self.gst.State.PAUSED
        if self.player.set_state(state) == self.gst.StateChangeReturn.FAILURE:
            self.fail('Audio output could not start')

    def set_mute(self, muted):
        self.muted = muted
        if self.available:
            self.player.set_property('mute', self.muted)

    def set_gain(self, gain, volume=VOLUME):
        if self.available:
            self.player.set_property('volume', volume*math.sin(gain*math.pi/2))

    def message(self, bus, message):
        if not self.available:
            return
        if message.type == self.gst.MessageType.ERROR:
            error, _ = message.parse_error()
            self.fail(error.message)
        elif message.type == self.gst.MessageType.EOS:
            if not self.player.seek_simple(self.gst.Format.TIME, self.gst.SeekFlags.FLUSH, 0):
                self.fail('Unable to loop the soundtrack')

    def fail(self, reason):
        self.error = reason
        print(f'jump.exe audio disabled: {reason}', file=sys.stderr)
        self.close()

    def close(self):
        if self.bus is not None:
            if self.watch is not None:
                self.bus.disconnect(self.watch)
            self.bus.remove_signal_watch()
            self.bus = self.watch = None
        if self.player is not None:
            self.player.set_state(self.gst.State.NULL)
            self.player = None
        self.active = False


class Music:
    def __init__(self, muted=False, tracks=TRACKS, sink_factory=None):
        self.muted = muted
        self.volume = VOLUME
        self.weights = [0.]*len(tracks)
        self.songs = {stage: Song(track, muted, sink_factory() if sink_factory else None)
                      for stage, track in enumerate(tracks) if track is not None}

    @property
    def available(self):
        return any(song.available for song in self.songs.values())

    def update(self, dt, stage, active):
        """Reverse a fade from its current mix; retain each song's play position."""
        step = max(0., dt)/FADE_SECONDS
        for index, song in self.songs.items():
            if not active:
                song.set_active(False)
                continue
            target = float(index == stage and song.available)
            old = self.weights[index]
            gain = min(target, old+step) if target > old else max(target, old-step)
            if gain < 1e-9:
                gain = 0.
            self.weights[index] = gain
            song.set_gain(gain, self.volume)
            song.set_active(gain > 0.)

    def adjust_volume(self, louder):
        """Audible 3 dB steps; keep the current fade and mute state intact."""
        self.volume = max(.005, min(1., self.volume*10**((3 if louder else -3)/20)))
        for index, song in self.songs.items():
            song.set_gain(self.weights[index], self.volume)

    def toggle_mute(self):
        self.muted = not self.muted
        for song in self.songs.values():
            song.set_mute(self.muted)

    def close(self):
        for song in self.songs.values():
            song.close()
