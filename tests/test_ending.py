import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
import cairo
from jump_exe.course import SUMMIT,WHITE_PILL
from jump_exe.ending import Ending,RESULT_AT,clock_text,in_world,focus_summit
from jump_exe.model import King,Tower,Camera,ledges
from jump_exe.story import Story,world_point
from jump_exe.devmode import DevMode
from jump_exe.finale_art import native,draw_finale,WIDTH,HEIGHT
from jump_exe.art import tile


class EndingTests(unittest.TestCase):
    def test_world_animation_precedes_results_and_frames_the_existing_summit(self):
        end=Ending();end.begin(90,50,0,hero_x=217)
        self.assertTrue(in_world(end.state()))
        self.assertEqual(end.state()['hero_x'],217)
        end.update(RESULT_AT)
        self.assertFalse(in_world(end.state()))
        for bounds in ((0,0,480,360),(0,0,1600,900),(0,0,2048,1152),(100,0,900,1600)):
            tower=Tower(bounds,42);camera=Camera(bounds)
            _,y,_,h=tower.rectangle(14)
            camera.offset=y+38*tower.scale-bounds[1]-bounds[3]*.38
            before=camera.offset
            focus_summit(camera,tower,1/60)
            self.assertLess(abs(camera.offset-before),20*tower.scale)
            for _ in range(180):focus_summit(camera,tower,1/60)
            self.assertGreaterEqual(y-camera.offset,bounds[1]+28-.1)
            self.assertLessEqual(y-camera.offset+h,bounds[1]+bounds[3])

    def test_summit_pickup_and_reactive_windows_use_the_same_native_pixels(self):
        from jump_exe.course import ROOMS
        for rank in (12,13,14):
            w,h=ROOMS[rank].rect[2:]
            for age in (.4,1.7,3.2,8.8):
                ending=dict(active=True,age=age,hero_x=217)
                pictures=[]
                for scale in (1,3):
                    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,w*scale,h*scale)
                    tile(cairo.Context(surface),w*scale,h*scale,rank,4,age,True,ending=ending)
                    surface.flush();pictures.append(bytes(surface.get_data()))
                source,scaled=pictures
                rows=[]
                for y in range(h):
                    row=source[y*w*4:(y+1)*w*4]
                    rows.append(b''.join(row[x*4:x*4+4]*3 for x in range(w))*3)
                self.assertEqual(scaled,b''.join(rows),(rank,age))

    def test_completion_is_one_shot_and_replay_keeps_earned_stats(self):
        end=Ending()
        self.assertTrue(end.begin(3661,417,2088))
        self.assertFalse(end.begin(1,1,1))
        snapshot=end.state()['stats']
        self.assertEqual(snapshot,dict(time='1:01:01',jumps=417,fall='5.8',practice=False))
        end.update(RESULT_AT)
        self.assertEqual(end.command('return'),'dismiss')
        end.update(100)
        end.replay()
        self.assertTrue(end.active)
        self.assertEqual(end.age,0)
        self.assertEqual(end.state()['stats'],snapshot)

    def test_enter_skips_then_dismisses_but_movement_never_skips(self):
        end=Ending();end.begin(90,50,0)
        self.assertIsNone(end.command('return'))
        end.update(2)
        for key in ('space','d','e','f2','r','n'):
            self.assertIsNone(end.command(key))
            self.assertTrue(end.active)
        self.assertEqual(end.command('return'),'skip')
        self.assertEqual(end.age,RESULT_AT)
        self.assertEqual(end.command('r'),'restart')
        self.assertEqual(end.command('n'),'new_seed')
        self.assertEqual(end.command('return'),'dismiss')

    def test_time_and_fall_tracking_freeze_at_collection_and_ignore_dev_flight(self):
        tower=Tower((0,0,1600,900),42);p=ledges(tower.near(0));king=King(1600,900)
        story=Story();king.enter(p)
        king.room=None;king.y=-2000
        story.update(1,king,tower)
        king.y=-1900;story.update(1,king,tower)
        king.land(p['0:floor'],p['0:floor'].left+100)
        story.update(1,king,tower)
        self.assertGreater(story.longest_fall,720)
        elapsed=story.play_seconds;drop=story.longest_fall
        story.update(30,king,tower,dev=True)
        self.assertEqual(story.play_seconds,elapsed)
        x,_=world_point(tower,*WHITE_PILL)
        king.land(p[SUMMIT],x);story.update(.1,king,tower)
        self.assertTrue(story.ending.active)
        self.assertTrue(story.ending.stats['practice'])
        snapshot=story.ending.state()['stats']
        king.room=None;king.y+=3000;story.update(20,king,tower)
        self.assertEqual(story.longest_fall,drop)
        self.assertEqual(story.ending.state()['stats'],snapshot)

    def test_finale_scales_as_native_pixels_and_stays_inside_its_window(self):
        stats=dict(time='1:23:45',jumps=999,fall='12.3',practice=True)
        for age in (0,1.5,4,9,13,18):
            end=dict(active=True,age=age,stats=stats)
            source=native(end);source.flush();data=bytes(source.get_data())
            out=cairo.ImageSurface(cairo.FORMAT_ARGB32,WIDTH*3+24,HEIGHT*3+56)
            draw_finale(cairo.Context(out),out.get_width(),out.get_height(),
                        dict(ending=end,sprite_scale=3,focused=True))
            out.flush();actual=bytes(out.get_data());stride=out.get_stride()
            self.assertFalse(any(actual[:28*stride]))
            for y in range(HEIGHT):
                row=data[y*WIDTH*4:(y+1)*WIDTH*4]
                expanded=b''.join(row[x*4:x*4+4]*3 for x in range(WIDTH))
                for dy in range(3):
                    begin=(28+y*3+dy)*stride+12*4
                    self.assertEqual(actual[begin:begin+len(expanded)],expanded)
        self.assertEqual(clock_text(59),'0:59')


class EndingIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Exercise the real app input/tick handlers without opening desktop windows.
        from jump_exe.main import App
        self.app=app=App.__new__(App)
        app.closed=False;app.ready=app.visible=app.focused=True
        app.bounds=(0,0,1600,900);app.seed=42;app.tower=Tower(app.bounds,42)
        app.platforms=ledges(app.tower.near(0));app.king=King(1600,900)
        app.king.land(app.platforms[SUMMIT],world_point(app.tower,*WHITE_PILL)[0])
        app.camera=Camera(app.bounds);app.dev=DevMode();app.keys=set()
        app.story=Story();app.story.update(0,app.king,app.tower)
        app.accepted=True;app.level=4;app.last=10.
        app.music=Mock(muted=False);app.sounds=Mock(clips={'complete':Mock()})
        app.place_windows=Mock();app.publish=Mock()

    def key(self,name,pressed=True):
        with patch('jump_exe.main.Gdk.keyval_name',return_value=name):
            self.app.key(None,SimpleNamespace(keyval=0),pressed)

    def test_finale_freezes_player_and_pauses_when_unfocused(self):
        app=self.app;before=(app.king.x,app.king.y,app.king.jumps)
        self.key('space');self.key('d');self.key('f2')
        with patch('jump_exe.main.time.monotonic',return_value=10.02):app.tick()
        self.assertEqual((app.king.x,app.king.y,app.king.jumps),before)
        self.assertFalse(app.dev.active)
        self.assertGreater(app.story.ending.age,0)
        age=app.story.ending.age;app.focused=False
        with patch('jump_exe.main.time.monotonic',return_value=10.04):app.tick()
        self.assertEqual(app.story.ending.age,age)

    def test_held_enter_cannot_skip_and_dismiss_in_one_press(self):
        app=self.app;app.story.ending.age=2
        self.key('Return');self.assertEqual(app.story.ending.age,RESULT_AT)
        self.key('Return');self.assertTrue(app.story.ending.active)
        self.key('Return',False);self.key('Return')
        self.assertFalse(app.story.ending.active)
        self.assertFalse(app.keys)
        self.key('e');self.assertTrue(app.story.ending.active)
        self.assertEqual(app.story.ending.age,0)

    def test_restart_clears_the_finale_and_completion_statistics(self):
        self.app.restart()
        self.assertFalse(self.app.story.accepted)
        self.assertFalse(self.app.story.ending.active)
        self.assertIsNone(self.app.story.ending.stats)


if __name__=='__main__':unittest.main()
