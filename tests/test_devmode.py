import unittest

from jump_exe.course import ROOMS
from jump_exe.devmode import DevMode
from jump_exe.model import King, Ledge, Tower, ledges
from jump_exe.physics_profile import PROFILE


class DevModeTests(unittest.TestCase):
    def setUp(self):
        self.bounds = (0,0,1600,900)
        self.tower = Tower(self.bounds,42)
        self.platforms = ledges(self.tower.near(0))
        self.king = King(*self.bounds[2:])
        self.king.enter(self.platforms)
        self.dev = DevMode()

    def test_enter_cancels_buffered_jump_momentum_and_landing_recovery(self):
        self.king.press()
        self.king.vx,self.king.vy = 400,1000
        self.king.recovery = .2
        self.king.accumulator = .008
        self.king.knocked = True
        before = self.king.x,self.king.y,self.king.jumps,self.king.falls
        self.dev.enter(self.king)
        self.assertEqual((self.king.x,self.king.y,self.king.jumps,self.king.falls),before)
        self.assertEqual((self.king.vx,self.king.vy,self.king.recovery,self.king.accumulator),(0,0,0,0))
        self.assertFalse(self.king.charging or self.king.jump_held or self.king.knocked)
        self.assertIsNone(self.king.room)

    def test_free_flight_crosses_solids_and_pauses_without_input(self):
        self.dev.enter(self.king)
        start_y = self.king.y
        for _ in range(20):
            self.dev.move(self.king,PROFILE.tick,{'s'},self.tower)
        self.assertGreater(self.king.y,start_y+50)
        point = self.king.x,self.king.y
        self.dev.move(self.king,.05,set(),self.tower)
        self.assertEqual((self.king.x,self.king.y),point)
        self.assertEqual(self.king.vy,0)

    def test_resume_on_floor_is_grounded_and_does_not_release_old_jump(self):
        self.king.press()
        point = self.king.x,self.king.y
        self.dev.enter(self.king)
        self.assertTrue(self.dev.resume(self.king,self.platforms))
        self.king.release(1)
        self.king.step(PROFILE.tick,self.platforms,0,self.bounds)
        self.assertEqual((self.king.x,self.king.y),point)
        self.assertEqual(self.king.room,'0:floor')
        self.assertEqual(self.king.jumps,0)

    def test_resume_inside_terrain_stays_in_flight_until_clear(self):
        self.dev.enter(self.king)
        self.king.y += 5
        self.assertFalse(self.dev.resume(self.king,self.platforms))
        self.assertTrue(self.dev.active)
        self.assertIsNone(self.dev.checkpoint)
        self.king.y -= 10
        self.assertTrue(self.dev.resume(self.king,self.platforms))
        self.assertFalse(self.dev.active)
        y = self.king.y
        self.king.step(PROFILE.tick,self.platforms,0,self.bounds)
        self.assertGreater(self.king.y,y)

    def test_retry_returns_to_exact_practice_position_with_fresh_motion(self):
        self.assertFalse(self.dev.retry(self.king,self.platforms))
        self.dev.enter(self.king)
        self.dev.skip_room(self.king,self.platforms,self.tower,8)
        self.king.facing = -1
        self.dev.resume(self.king,self.platforms)
        point = self.king.x,self.king.y,self.king.facing,self.king.room
        self.king.press()
        self.king.release(1)
        self.king.step(.05,self.platforms,0,self.bounds)
        self.assertTrue(self.dev.retry(self.king,self.platforms))
        self.assertEqual((self.king.x,self.king.y,self.king.facing,self.king.room),point)
        self.assertEqual((self.king.vx,self.king.vy),(0,0))
        self.assertEqual(self.king.jumps,1)
        self.assertFalse(self.dev.active or self.king.jump_held)

    def test_every_room_can_be_selected_and_resumed_without_overlaps(self):
        for bounds in ((0,0,1600,900),(-900,100,900,1600)):
            for seed in (0,42,9876):
                tower = Tower(bounds,seed)
                platforms = ledges(tower.near(0))
                king = King(*bounds[2:])
                king.enter(platforms)
                dev = DevMode()
                for index in range(len(ROOMS)):
                    with self.subTest(bounds=bounds,seed=seed,room=index):
                        dev.enter(king)
                        self.assertTrue(dev.skip_room(king,platforms,tower,0 if index==0 else 1))
                        self.assertEqual(dev.selected_room,index)
                        self.assertTrue(dev.resume(king,platforms))
                        king.step(PROFILE.tick,platforms,0,bounds)
                        self.assertEqual(king.room,f'{index}:{ROOMS[index].route[0]}')
                        self.assertTrue(dev.clear_at(king,platforms))

    def test_room_selection_clamps_at_course_ends(self):
        self.dev.enter(self.king)
        self.assertTrue(self.dev.skip_room(self.king,self.platforms,self.tower,-1))
        self.assertEqual(self.dev.selected_room,0)
        self.assertTrue(self.dev.skip_room(self.king,self.platforms,self.tower,100))
        self.assertEqual(self.dev.selected_room,len(ROOMS)-1)
        self.assertTrue(self.dev.skip_room(self.king,self.platforms,self.tower,1))
        self.assertEqual(self.dev.selected_room,len(ROOMS)-1)

    def test_diagonal_flight_is_normalized_and_modifiers_adjust_speed(self):
        distances = []
        for keys in ({'w'},{'w','d'},{'w','shift_l'},{'w','control_l'}):
            self.king.enter(self.platforms)
            self.dev.enter(self.king)
            x,y = self.king.x,self.king.y
            self.dev.move(self.king,.05,keys,self.tower)
            distances.append(((self.king.x-x)**2+(self.king.y-y)**2)**.5)
        self.assertAlmostEqual(distances[0],distances[1])
        self.assertAlmostEqual(distances[2],distances[0]*4)
        self.assertAlmostEqual(distances[3],distances[0]*.25)

    def test_side_and_underside_overlap_prevent_invalid_resumes(self):
        p = {'wall':Ledge('wall',100,200,300,50)}
        self.assertFalse(self.dev.clear_at(self.king,p,100-self.king.half+1,320))
        self.assertFalse(self.dev.clear_at(self.king,p,150,350+self.king.body_height-1))
        self.assertTrue(self.dev.clear_at(self.king,p,150,300))
        self.assertTrue(self.dev.clear_at(self.king,p,100-self.king.half,320))


if __name__ == '__main__':
    unittest.main()
