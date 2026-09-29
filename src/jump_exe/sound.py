"""Short, preloaded jump and landing cues driven by actual character movement."""
from .music import ASSETS, Song


CLIPS = {'jump': ASSETS/'sfx/jump.wav',
         'land': ASSETS/'sfx/land.wav',
         'heavy_land': ASSETS/'sfx/heavy_land.wav',
         'complete': ASSETS/'sfx/white_pill.wav'}
VOLUME = .65


class Effect(Song):
    def __init__(self, path, audio_sink=None):
        super().__init__(path, audio_sink=audio_sink)
        if self.available:
            self.player.set_property('volume', VOLUME)
            # Decode and preroll once so the first jump has no file-open delay.
            if self.player.set_state(self.gst.State.PAUSED) == self.gst.StateChangeReturn.FAILURE:
                self.fail('Unable to preload sound effect')

    def play(self):
        if not self.available:
            return
        if not self.player.seek_simple(self.gst.Format.TIME, self.gst.SeekFlags.FLUSH, 0):
            # A very early trigger can arrive before initial preroll completes.
            self.player.set_state(self.gst.State.READY)
            self.active = False
        self.set_active(True)

    def stop(self):
        if self.available and self.active:
            self.set_active(False)
            if self.available:
                self.player.seek_simple(self.gst.Format.TIME, self.gst.SeekFlags.FLUSH, 0)

    def message(self, bus, message):
        if self.available and message.type == self.gst.MessageType.EOS:
            self.stop()
        else:
            super().message(bus, message)


class SoundEffects:
    def __init__(self, sink_factory=None):
        self.clips = {name: Effect(path, sink_factory() if sink_factory else None)
                      for name, path in CLIPS.items()}
        self.previous = None

    def sync(self, king):
        """Teleports, practice mode and restarts are silent."""
        self.stop()
        self.previous = (king.jumps, king.room)

    def update(self, king, active=True):
        current = (king.jumps, king.room)
        if not active or self.previous is None:
            self.sync(king)
            return ()
        jumps, room = self.previous
        events = []
        if king.jumps > jumps:
            events.append('jump')
        if king.room is not None and king.room != room:
            events.append('heavy_land' if king.recovery > 0 else 'land')
        self.previous = current
        for event in events:
            self.clips[event].play()
        return tuple(events)

    def stop(self):
        for clip in self.clips.values():
            clip.stop()

    def celebrate(self,muted=False):
        clip=self.clips['complete']
        clip.set_mute(muted)
        if not muted:clip.play()

    def close(self):
        for clip in self.clips.values():
            clip.close()
