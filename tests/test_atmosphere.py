import copy
import json
import unittest
import cairo

from jump_exe.atmosphere import Atmosphere
from jump_exe.atmosphere_art import BUILD_AREAS
from jump_exe.art import tile,knight
from jump_exe.character import reacted_frame
from jump_exe.course import ROOMS
from jump_exe.model import King,Tower,ledges
from jump_exe.physics_profile import PROFILE
from jump_exe.story import Story


class AtmosphereTests(unittest.TestCase):
    def setUp(self):
        self.bounds=(0,0,480,360)
        self.tower=Tower(self.bounds,42)
        self.p=ledges(self.tower.near(0))
        self.king=King(480,360)
        self.fx=Atmosphere()

    def go(self,key,fraction=.5):
        p=self.p[key]
        self.king.land(p,p.left+(p.right-p.left)*fraction)

    def step(self,count=1,enabled=True):
        for _ in range(count):self.fx.update(PROFILE.tick,self.king,self.tower,enabled)

    def test_stage_reactions_and_neighbor_wakeup_have_cooldowns(self):
        for rank,key in ((0,'0:home'),(4,'4:valve'),(6,'6:pan'),(11,'11:entry'),(12,'12:branch')):
            self.fx=Atmosphere();self.go(key);self.step()
            state=self.fx.room(rank)
            self.assertAlmostEqual(state['wake'],0)
            self.assertAlmostEqual(self.fx.room(rank+1)['wake'],0)
            self.assertIn('light',self.fx.avatar)
            self.step(120)
            self.assertAlmostEqual(self.fx.room(rank)['wake'],2)
            if rank==4:
                self.assertAlmostEqual(state['vent'],0)
                self.assertAlmostEqual(state['arc'],0)
                self.assertTrue(any(p['kind']=='paper' for p in state['particles']))
            if rank==6:self.assertGreaterEqual(self.fx.room(rank)['scan'],1.4)
            if rank==12:self.assertAlmostEqual(state['build'],0)

    def test_denial_suggestion_breaks_into_text_at_the_actual_landing(self):
        self.go('0:home');self.step()
        self.king.press();self.king.charge=20/36;self.king.release(1);self.step()
        self.assertEqual(self.fx.room(0)['echo']['direction'],-1)
        self.go('0:spacebar');self.step()
        self.assertIsNone(self.fx.room(0)['echo'])
        self.assertTrue(any(p['kind']=='text' for p in self.fx.room(0)['particles']))

    def test_hard_landing_throws_directional_debris_and_settles_clothing(self):
        self.go('4:valve')
        self.king.room=None;self.king.vx=200;self.king.vy=700;self.step()
        self.go('4:valve');self.step(3)
        particles=self.fx.room(4)['particles']
        screws=[p for p in particles if p['kind']=='screw']
        self.assertTrue(screws)
        self.assertGreater(sum(p['vx'] for p in screws)/len(screws),0)
        self.assertNotEqual(self.fx.avatar['settle'],0)

    def test_papers_settle_on_hardware_and_particle_history_is_bounded(self):
        self.go('6:pan');self.step()
        state=self.fx.rooms[6]
        block=next(b for b in ROOMS[6].blocks if b.name=='pan')
        state['particles']=[dict(kind='paper',x=40,y=block.y-8,vx=0,vy=24,
                                 life=4,settled=False,glyph=';')]
        self.step(30)
        p=self.fx.room(6)['particles'][0]
        self.assertTrue(p['settled']);self.assertEqual(p['y'],block.y-1)
        for _ in range(50):self.fx.spawn(6,'paper',40,200,10)
        self.assertLessEqual(len(self.fx.room(6)['particles']),48)
        self.step(600)
        self.assertFalse(self.fx.room(6)['particles'])
        self.assertLessEqual(len(self.fx.history),32)

    def test_depression_reflection_follows_an_older_position(self):
        self.go('11:entry',.4);self.step(30)
        old_x=self.fx.room(11)['hero']['x']
        self.king.x+=16;self.step(2)
        self.assertAlmostEqual(self.fx.room(11)['reflection']['x'],old_x)
        self.assertGreater(self.fx.room(11)['hero']['x'],old_x)

    def test_development_mode_and_ending_clear_transient_effects(self):
        self.go('4:valve');self.step(50)
        self.assertTrue(self.fx.avatar)
        self.step(enabled=False)
        self.assertFalse(self.fx.avatar)
        self.assertEqual(self.fx.room(4),{})
        self.assertFalse(self.fx.history)
        self.step()
        self.assertAlmostEqual(self.fx.room(4)['vent'],0)
        self.assertEqual(self.fx.avatar['settle'],0)
        story=Story();story.ending.begin(1,1,1)
        story.update(PROFILE.tick,self.king,self.tower)
        self.assertFalse(story.state(0)['avatar_fx'])
        fresh=Atmosphere()
        self.assertGreater(fresh.room(4)['wake'],6)

    def test_real_physics_and_terrain_are_identical_with_effects_running(self):
        self.go('0:home')
        other=copy.deepcopy(self.king);terrain=copy.deepcopy(self.p)
        self.king.press();other.press()
        for _ in range(20):
            self.king.step(PROFILE.tick,self.p,0,self.bounds)
            other.step(PROFILE.tick,self.p,0,self.bounds)
            self.fx.update(PROFILE.tick,self.king,self.tower)
        self.king.release(1);other.release(1)
        for _ in range(240):
            self.king.step(PROFILE.tick,self.p,0,self.bounds)
            other.step(PROFILE.tick,self.p,0,self.bounds)
            self.fx.update(PROFILE.tick,self.king,self.tower)
            self.assertEqual(vars(self.king),vars(other))
        self.assertEqual(self.p,terrain)
        json.dumps(dict(avatar_fx=self.fx.avatar,ambient=self.fx.room(0)))

    def test_tiny_build_previews_are_clear_of_all_solid_platforms(self):
        for rank,(x,y,w) in BUILD_AREAS.items():
            for block in ROOMS[rank].blocks:
                overlap=(x<block.x+block.w and x+w>block.x
                         and y<block.y+block.h and y+40>block.y)
                self.assertFalse(overlap,(rank,block.name))

    def test_reactive_rooms_and_character_share_the_native_pixel_grid(self):
        for rank,room in enumerate(ROOMS):
            self.fx=Atmosphere();self.go(f'{rank}:{room.route[0]}')
            self.step(50)
            self.fx.spawn(rank,'paper',20,40,3)
            w,h=room.rect[2:];pictures=[]
            for scale in (1,3):
                surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,w*scale,h*scale)
                tile(cairo.Context(surface),w*scale,h*scale,rank,rank//3,.8,
                     ambient=self.fx.room(rank))
                surface.flush();pictures.append(bytes(surface.get_data()))
            original,scaled=pictures
            expected=b''.join(b''.join(original[(y*w+x)*4:(y*w+x+1)*4]*3
                                       for x in range(w))*3 for y in range(h))
            self.assertEqual(scaled,expected,rank)
        for fx in (dict(light=(1,.2,.1),strength=.3,wind=1,settle=-1,scan=-1),
                   dict(light=(.4,.8,1),strength=.1,wind=0,settle=0,scan=.5)):
            pictures=[]
            for scale in (1,3):
                surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,40*scale,40*scale)
                knight(cairo.Context(surface),20*scale,36*scale,1,0,0,scale,'idle',fx)
                surface.flush();pictures.append(bytes(surface.get_data()))
            source,scaled=pictures
            expected=b''.join(b''.join(source[(y*40+x)*4:(y*40+x+1)*4]*3
                                       for x in range(40))*3 for y in range(40))
            self.assertEqual(scaled,expected)
        self.assertLessEqual(reacted_frame.cache_info().currsize,384)


if __name__=='__main__':unittest.main()
