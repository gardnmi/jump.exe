import time
import unittest
from unittest.mock import Mock, patch
import warnings

from jump_exe.model import King, Ledge
from jump_exe.physics_profile import PROFILE
from jump_exe.sound import CLIPS, Effect, SoundEffects

try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst, GLib
    Gst.init(None)
except (ImportError, ValueError):
    Gst = None


class MovementSoundTests(unittest.TestCase):
    def setUp(self):
        with patch('jump_exe.sound.Effect', side_effect=lambda *args: Mock()):
            self.sounds = SoundEffects()
        self.king = King(480, 360)
        self.platforms = {'floor': Ledge('floor', 0, 480, 300)}
        self.king.enter(self.platforms)
        self.sounds.sync(self.king)

    def advance(self, frames):
        cues = []
        for _ in range(frames):
            self.king.step(PROFILE.tick, self.platforms, 0, (0, 0, 480, 360))
            cues.extend(self.sounds.update(self.king))
        return cues

    def test_spawn_standing_and_cancelled_charge_are_silent(self):
        self.assertEqual(self.advance(3), [])
        self.king.press()
        self.assertEqual(self.advance(3), [])
        self.king.cancel()
        self.assertEqual(self.advance(3), [])
        for clip in self.sounds.clips.values():
            clip.play.assert_not_called()

    def test_real_jump_and_landing_each_play_once(self):
        self.king.press()
        self.advance(8)
        self.king.release(0)
        self.assertEqual(self.sounds.update(self.king), ('jump',))
        self.assertEqual(self.sounds.update(self.king), ())
        self.assertEqual(self.advance(120), ['land'])
        self.sounds.clips['jump'].play.assert_called_once()
        self.sounds.clips['land'].play.assert_called_once()
        self.sounds.clips['heavy_land'].play.assert_not_called()

    def test_heavy_fall_plays_splat_instead_of_normal_landing(self):
        self.king.room = None
        self.king.y, self.king.vy = 275, 850
        self.sounds.sync(self.king)
        self.assertEqual(self.advance(90), ['heavy_land'])
        self.sounds.clips['heavy_land'].play.assert_called_once()
        self.sounds.clips['land'].play.assert_not_called()
        self.sounds.clips['jump'].play.assert_not_called()

    def test_practice_moves_and_restart_do_not_replay_events(self):
        self.king.press()
        self.king.release(0)
        self.assertEqual(self.sounds.update(self.king, active=False), ())
        self.assertEqual(self.sounds.update(self.king), ())
        self.king.reset(self.platforms)
        self.sounds.sync(self.king)
        self.assertEqual(self.sounds.update(self.king), ())
        for clip in self.sounds.clips.values():
            clip.play.assert_not_called()

    def test_completion_cue_respects_mute_and_is_not_a_movement_event(self):
        self.sounds.celebrate(muted=True)
        self.sounds.clips['complete'].play.assert_not_called()
        self.sounds.celebrate(muted=False)
        self.sounds.clips['complete'].play.assert_called_once()
        self.sounds.clips['complete'].set_mute.assert_called_with(False)


@unittest.skipIf(Gst is None, 'GStreamer is optional')
class EffectPlaybackTests(unittest.TestCase):
    def test_real_clips_decode_finish_replay_and_release_their_players(self):
        self.enterContext(warnings.catch_warnings())
        warnings.filterwarnings('ignore',
            message=r"'asyncio\.(get_event_loop_policy|AbstractEventLoopPolicy)' is deprecated",
            category=DeprecationWarning, module=r'gi\.events')
        for name in ('playbin', 'wavparse', 'fakesink'):
            if Gst.ElementFactory.find(name) is None:
                self.skipTest(f'Optional GStreamer plugin unavailable: {name}')
        context = GLib.MainContext.default()

        def wait_for(predicate):
            deadline = time.monotonic()+3
            while time.monotonic() < deadline:
                while context.pending():
                    context.iteration(False)
                if predicate():
                    return
                time.sleep(.005)
            self.fail('Sound effect did not complete within three seconds')

        for name, path in CLIPS.items():
            with self.subTest(clip=name):
                decoded = []
                sink = Gst.ElementFactory.make('fakesink')
                sink.set_property('sync', True)
                sink.set_property('signal-handoffs', True)
                sink.connect('handoff', lambda _sink, buffer, _pad: decoded.append(buffer.get_size()))
                clip = Effect(path, audio_sink=sink)
                self.addCleanup(clip.close)
                self.assertTrue(clip.available)
                player = clip.player
                self.assertEqual(player.get_state(Gst.SECOND)[1], Gst.State.PAUSED)
                clip.play()
                wait_for(lambda: not clip.active)
                self.assertIsNone(clip.error)
                self.assertGreater(sum(decoded), 0)
                self.assertEqual(player.get_state(Gst.SECOND)[1], Gst.State.PAUSED)
                count = len(decoded)
                clip.play()
                wait_for(lambda: len(decoded) > count)
                clip.stop()
                self.assertFalse(clip.active)
                clip.close()
                self.assertEqual(player.get_state(Gst.SECOND)[1], Gst.State.NULL)


if __name__ == '__main__':
    unittest.main()
