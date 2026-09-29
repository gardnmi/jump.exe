"""Exercise actual decoding and crossfades without opening an audio device."""
from contextlib import redirect_stderr
import array
import io
import math
import sys
from pathlib import Path
import tempfile
import time
import unittest
import warnings

from jump_exe.music import Music, TRACKS, FADE_SECONDS

try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst, GLib
    Gst.init(None)
except (ImportError, ValueError):
    Gst = None


@unittest.skipIf(Gst is None, 'GStreamer is optional')
class MusicTests(unittest.TestCase):
    def setUp(self):
        # PyGObject's context iterator emits this on every call with Python 3.14.
        self.enterContext(warnings.catch_warnings())
        warnings.filterwarnings('ignore', message="'asyncio.get_event_loop_policy' is deprecated",
                                category=DeprecationWarning, module=r'gi\.events')
        for name in ('playbin', 'opusdec', 'oggdemux', 'fakesink'):
            if Gst.ElementFactory.find(name) is None:
                self.skipTest(f'Optional GStreamer plugin unavailable: {name}')
        self.music = Music(sink_factory=self.sink)
        self.addCleanup(self.music.close)

    @staticmethod
    def sink():
        sink = Gst.ElementFactory.make('fakesink')
        sink.set_property('sync', True)
        return sink

    def wait_for(self, predicate):
        deadline = time.monotonic()+3
        context = GLib.MainContext.default()
        while time.monotonic() < deadline:
            while context.pending():
                context.iteration(False)
            if predicate():
                return
            time.sleep(.005)
        self.fail('Audio condition did not complete within three seconds')

    def player(self, stage):
        return self.music.songs[stage].player

    def position(self, stage):
        return self.player(stage).query_position(Gst.Format.TIME)[1]/Gst.SECOND

    def playing(self, stage):
        result, state, _ = self.player(stage).get_state(2*Gst.SECOND)
        self.assertEqual(result, Gst.StateChangeReturn.SUCCESS)
        self.assertEqual(state, Gst.State.PLAYING)

    def test_crossfade_reverses_without_restarting_either_song(self):
        stages = list(self.music.songs)
        for source, target in zip(stages, stages[1:]):
            with self.subTest(source=source, target=target):
                self.music.update(FADE_SECONDS, source, True)
                self.playing(source)
                self.assertTrue(self.player(source).seek_simple(
                    Gst.Format.TIME, Gst.SeekFlags.FLUSH, 17*Gst.SECOND))
                self.playing(source)
                self.music.update(.8, target, True)
                self.playing(target)
                before = [self.player(i).get_property('volume') for i in (source, target)]
                self.music.update(.2, source, True)
                after = [self.player(i).get_property('volume') for i in (source, target)]
                self.assertGreater(after[0], before[0])
                self.assertLess(after[1], before[1])
                self.assertTrue(all(self.music.songs[i].active for i in (source, target)))
                self.music.update(FADE_SECONDS, target, True)
                self.assertFalse(self.music.songs[source].active)
                self.music.update(FADE_SECONDS, source, True)
                self.playing(source)
                self.assertGreaterEqual(self.position(source), 17.)

    def test_pause_freezes_playhead_and_mix_mute_survives_resume_and_close_stops(self):
        self.music.update(FADE_SECONDS, 0, True)
        self.playing(0)
        self.wait_for(lambda: self.position(0) > .05)
        self.music.update(.5, 1, True)
        self.playing(1)
        self.music.update(.1, 1, False)
        players = [song.player for song in self.music.songs.values()]
        for stage, song in self.music.songs.items():
            expected = Gst.State.PAUSED if stage in (0, 1) else Gst.State.NULL
            self.assertEqual(song.player.get_state(Gst.SECOND)[1], expected)
        positions = [self.position(i) for i in (0, 1)]
        weights = self.music.weights.copy()
        time.sleep(.08)
        self.music.update(FADE_SECONDS, 0, False)
        self.assertEqual(self.music.weights, weights)
        for i in (0, 1):
            self.assertAlmostEqual(self.position(i), positions[i], places=3)
        self.music.toggle_mute()
        self.music.update(.1, 0, True)
        self.assertTrue(all(p.get_property('mute') for p in players))
        self.music.close()
        self.music.close()
        for player in players:
            self.assertEqual(player.get_state(Gst.SECOND)[1], Gst.State.NULL)

    def test_all_real_files_loop_after_end_of_stream(self):
        for stage in self.music.songs:
            with self.subTest(stage=stage):
                self.music.update(FADE_SECONDS, stage, True)
                self.playing(stage)
                player = self.player(stage)
                ok, duration = player.query_duration(Gst.Format.TIME)
                self.assertTrue(ok)
                self.assertGreater(duration, 190*Gst.SECOND)
                self.assertTrue(player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH,
                                                  duration-int(.1*Gst.SECOND)))
                self.playing(stage)
                self.wait_for(lambda: 0 <= self.position(stage) < 2)
                self.assertIsNone(self.music.songs[stage].error)
                self.assertTrue(self.music.songs[stage].active)

    def test_music_reduction_reaches_decoded_audio_for_every_stage(self):
        if Gst.ElementFactory.find('appsink') is None:
            self.skipTest('Optional GStreamer appsink unavailable')

        def rms(track, volume=None):
            sink = Gst.ElementFactory.make('appsink')
            sink.set_property('sync', False)
            sink.set_property('max-buffers', 4)
            sink.set_property('caps', Gst.Caps.from_string(
                'audio/x-raw,format=F32LE,layout=interleaved,rate=48000,channels=2'))
            music = Music(tracks=(track,), sink_factory=lambda: sink)
            try:
                if volume is not None:
                    music.volume = volume
                music.update(FADE_SECONDS, 0, True)
                squares = 0.
                count = 0
                while count < 96000:
                    sample = sink.emit('try-pull-sample', 2*Gst.SECOND)
                    self.assertIsNotNone(sample, 'Decoder produced no audio')
                    buffer = sample.get_buffer()
                    samples = array.array('f', buffer.extract_dup(0, buffer.get_size()))
                    if sys.byteorder != 'little':
                        samples.byteswap()
                    squares += sum(value*value for value in samples)
                    count += len(samples)
                return math.sqrt(squares/count)
            finally:
                music.close()

        for track in TRACKS:
            with self.subTest(track=track.name):
                previous = rms(track, .288)
                self.assertGreater(previous, 0.)
                self.assertAlmostEqual(rms(track)/previous, .5, places=4)

    def test_volume_controls_adjust_both_fading_tracks_without_changing_mix_or_mute(self):
        self.music.update(FADE_SECONDS, 0, True)
        self.music.update(.8, 1, True)
        self.music.toggle_mute()
        before = [self.player(i).get_property('volume') for i in (0, 1)]
        weights = self.music.weights.copy()
        self.music.adjust_volume(False)
        for stage in (0, 1):
            self.assertAlmostEqual(self.player(stage).get_property('volume')/before[stage],
                                   10**(-3/20), places=5)
            self.assertTrue(self.player(stage).get_property('mute'))
        self.assertEqual(weights, self.music.weights)
        self.music.update(0, 1, True)
        self.music.adjust_volume(True)
        for stage in (0, 1):
            self.assertAlmostEqual(self.player(stage).get_property('volume'), before[stage])
        for louder in (True, False):
            for _ in range(100):
                self.music.adjust_volume(louder)
            self.assertAlmostEqual(self.music.volume, 1. if louder else .005)

    def test_unassigned_stages_fade_to_quiet_and_can_return(self):
        music = Music(tracks=(TRACKS[0], None), sink_factory=self.sink)
        self.addCleanup(music.close)
        music.update(FADE_SECONDS, 0, True)
        music.update(.5, 1, True)
        self.assertGreater(music.weights[0], 0.)
        music.update(FADE_SECONDS, 1, True)
        self.assertEqual(music.weights, [0., 0.])
        self.assertFalse(any(song.active for song in music.songs.values()))
        music.update(.5, 0, True)
        self.assertTrue(music.songs[0].active)

    def test_bad_track_disables_only_that_song(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            path = Path(directory)/'invalid.opus'
            path.write_bytes(b'not audio')
            music = Music(tracks=(TRACKS[0], path), sink_factory=self.sink)
            self.addCleanup(music.close)
            music.update(FADE_SECONDS, 1, True)
            self.wait_for(lambda: music.songs[1].error is not None)
            self.assertTrue(music.available)
            music.update(FADE_SECONDS, 0, True)
            self.assertTrue(music.songs[0].active)
            music.close()


if __name__ == '__main__':
    unittest.main()
