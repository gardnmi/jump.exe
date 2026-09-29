import unittest
from jump_exe.model import King, Ledge, ledges, Tower, Camera, ROOM_COUNT, room_geometry, exposed_top
from jump_exe.course import ROOMS, ROUTE, START, SUMMIT
from jump_exe.routecheck import solve, audit_falls, find_jump, launch, replay_step
from jump_exe.physics_profile import PROFILE


def jump_trial(bounds, platforms, source, local, frames, direction):
    king = King(*bounds[2:])
    p = platforms[source]
    king.land(p,p.left+(p.right-p.left)*local)
    king.press()
    for _ in range(frames):
        king.step(PROFILE.tick,platforms,0,bounds)
    king.release(direction)
    bounced = False
    for _ in range(180):
        vx = king.vx
        king.step(PROFILE.tick,platforms,0,bounds)
        bounced |= vx*king.vx < 0
        if king.room is not None:
            break
    return king,bounced


class PhysicsTests(unittest.TestCase):
    def setUp(self):
        self.p = {'start':Ledge('start',0,400,700),'upper':Ledge('upper',450,850,400)}
        self.k = King(1000,900)
        self.k.reset(self.p)
        self.bounds = (0,0,1000,900)

    def step(self, count, direction=0):
        for _ in range(count):
            self.k.step(1/120,self.p,direction,self.bounds)

    def test_charge_saturates_and_repeat_does_not_reset(self):
        self.k.press()
        self.step(60)
        charge = self.k.charge
        self.k.press()
        self.assertEqual(self.k.charge,charge)
        self.step(200)
        self.assertEqual(self.k.charge,1)

    def test_full_charge_is_exactly_36_frames_and_does_not_auto_release(self):
        self.k.press()
        self.step(70)
        self.assertAlmostEqual(self.k.charge,35/36)
        self.step(2)
        self.assertEqual(self.k.charge,1)
        self.step(120)
        self.assertEqual(self.k.room,'start')
        self.assertEqual(self.k.jumps,0)
        self.k.release(1)
        self.assertEqual(self.k.vy,-PROFILE.jump_y_max*self.k.scale)

    def test_tap_is_a_small_jump_and_release_selects_direction(self):
        self.k.press()
        self.k.release(-1)
        self.assertEqual(self.k.vy,-PROFILE.jump_y_min*self.k.scale)
        self.assertLess(self.k.vx,0)
        self.assertEqual(self.k.facing,-1)

    def test_held_jump_buffers_charge_after_landing(self):
        self.k.room = None
        self.k.x,self.k.y,self.k.vy = 200,680,50
        self.k.press()
        self.assertFalse(self.k.charging)
        self.step(40)
        self.assertEqual(self.k.room,'start')
        self.assertTrue(self.k.charging)
        self.assertGreater(self.k.charge,0)

    def test_released_airborne_input_does_not_jump_on_landing(self):
        self.k.room = None
        self.k.x,self.k.y,self.k.vy = 200,680,50
        self.k.press()
        self.k.release(1)
        self.step(40)
        self.assertEqual(self.k.room,'start')
        self.assertFalse(self.k.charging)
        self.assertEqual(self.k.jumps,0)

    def test_hard_landing_recovers_before_walking_or_buffered_charge(self):
        self.k.room = None
        self.k.x,self.k.y,self.k.vy = 200,680,1800
        self.k.press()
        self.step(4)
        self.assertEqual(self.k.room,'start')
        self.assertEqual(self.k.pose,'land')
        x = self.k.x
        self.step(12,1)
        self.assertEqual(self.k.x,x)
        self.assertFalse(self.k.charging)
        self.step(40)
        self.assertTrue(self.k.charging)
        self.assertEqual(self.k.pose,'charge')

    def test_render_rate_does_not_change_trajectory(self):
        results = []
        for fps in (30,60,120,144):
            k = King(1000,900)
            k.reset(self.p)
            k.press()
            for _ in range(fps//2):
                k.step(1/fps,self.p,0,self.bounds)
            k.release(1)
            for _ in range(fps//2):
                k.step(1/fps,self.p,-1,self.bounds)
            results.append((k.x,k.y,k.vx,k.vy))
        for state in results[1:]:
            for value,expected in zip(state,results[0]):
                self.assertAlmostEqual(value,expected,places=6)

    def test_uniform_scale_preserves_jump_shape_and_knight_proportions(self):
        results = []
        for width,height in ((1600,900),(900,1600),(1920,1080)):
            k = King(width,height)
            s = k.scale
            ps = {'start':Ledge('start',40*s,150*s,300*s)}
            k.reset(ps)
            start_x,start_y = k.x,k.y
            k.press()
            k.charge = 1
            k.release(1)
            for _ in range(20):
                k.step(1/60,ps,0,(0,0,width,height))
            results.append(((k.x-start_x)/s,(k.y-start_y)/s,k.body_height/s))
        for actual in results[1:]:
            for a,b in zip(actual,results[0]):
                self.assertAlmostEqual(a,b,places=6)

    def test_lands_on_higher_window(self):
        self.k.press()
        self.step(100)
        self.k.release(1)
        self.step(130)
        self.assertEqual(self.k.room,'upper')
        self.assertEqual(self.k.y,400)

    def test_no_air_steering(self):
        self.k.press()
        self.step(100)
        self.k.release(1)
        vx = self.k.vx
        self.step(10,-1)
        self.assertEqual(self.k.vx,vx)

    def test_fall_can_land_on_lower_window(self):
        self.k.room = None
        self.k.x,self.k.y,self.k.vy = 200,300,1000
        self.step(70)
        self.assertEqual(self.k.room,'start')
        self.assertEqual(self.k.falls,0)

    def test_swept_landing_on_narrow_ledge(self):
        self.p = {'tiny':Ledge('tiny',495,505,500)}
        self.k.room = None
        self.k.x,self.k.y,self.k.vx,self.k.vy = 490,490,2000,2000
        self.k.step(.05,self.p,0,self.bounds)
        self.assertEqual(self.k.room,'tiny')

    def test_walking_off_edge_starts_a_fall(self):
        self.k.local = 399
        self.step(12,1)
        self.assertIsNone(self.k.room)
        self.assertGreater(self.k.y,700)

    def test_offscreen_respawns(self):
        self.k.room = None
        self.k.x,self.k.y = 900,980
        self.step(2)
        self.assertEqual(self.k.room,'start')
        self.assertEqual(self.k.falls,1)

    def test_standing_character_follows_window_move(self):
        old_x = self.k.x
        self.p['start'] = Ledge('start',80,480,650)
        self.step(2)
        self.assertEqual(self.k.x,old_x+80)
        self.assertEqual(self.k.y,650)

    def test_walk_then_charge_locks_feet(self):
        x = self.k.x
        self.step(24,1)
        self.assertGreater(self.k.x,x)
        self.assertTrue(self.k.walking)
        x = self.k.x
        self.k.press()
        self.step(60,-1)
        self.assertEqual(self.k.x,x)
        self.assertEqual(self.k.facing,-1)
        self.k.release(-1)
        self.step(2)
        self.assertLess(self.k.x,x)
        self.assertIsNone(self.k.room)

    def test_top_edge_does_not_interrupt_trajectory(self):
        self.k.room = None
        self.k.x,self.k.y,self.k.vy = 200,-10,-500
        self.step(2)
        self.assertLess(self.k.y,-12)
        self.assertLess(self.k.vy,0)
        self.assertIsNone(self.k.room)
        self.assertEqual(self.k.falls,0)

    def test_fall_from_upper_section_can_land_in_previous_section(self):
        self.p = {'earlier':Ledge('earlier',100,300,-200),
                  'higher':Ledge('higher',500,800,-600)}
        self.k.room = None
        self.k.x,self.k.y,self.k.vy = 200,-650,400
        self.step(90)
        self.assertEqual(self.k.room,'earlier')
        self.assertEqual(self.k.y,-200)
        self.assertEqual(self.k.falls,0)

    def test_monitor_offset_used_by_ledges(self):
        p = ledges({'0':(1920,200,600,300)})['0:floor']
        self.assertEqual(p,Ledge('0:floor',1920,2520,478,22))

    def test_walking_into_wall_stops_without_penetration(self):
        self.p['wall'] = Ledge('wall',300,320,500,220)
        self.k.land(self.p['start'],270)
        self.step(60,1)
        self.assertAlmostEqual(self.k.x+self.k.half,300,delta=.02)
        self.assertEqual(self.k.room,'start')

    def test_side_hit_bounces_and_preserves_fall(self):
        self.p = {'wall':Ledge('wall',300,330,300,240)}
        self.k.room = None
        self.k.x,self.k.y,self.k.vx,self.k.vy = 280,400,500,-100
        self.step(4)
        self.assertLess(self.k.vx,0)
        self.assertLess(self.k.x,290)
        self.assertIsNone(self.k.room)

    def test_head_bonk_stops_upward_jump(self):
        self.p = {'ledge':Ledge('ledge',100,300,300)}
        self.k.room = None
        self.k.x,self.k.y,self.k.vx,self.k.vy = 200,380,0,-700
        self.step(5)
        self.assertGreater(self.k.vy,0)
        self.assertGreaterEqual(self.k.y,366)
        self.assertIsNone(self.k.room)

    def test_fast_wall_impact_does_not_tunnel(self):
        self.p = {'wall':Ledge('wall',400,410,100,600)}
        self.k.room = None
        self.k.x,self.k.y,self.k.vx,self.k.vy = 200,400,10000,0
        self.k.step(.05,self.p,0,self.bounds)
        self.assertLess(self.k.x,390)
        self.assertLess(self.k.vx,0)



class TowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = solve(seed=42)
        cls.falls = audit_falls(cls.route,seed=42)

    def test_room_shapes_and_window_footprints_are_authored_individually(self):
        self.assertGreater(len({room.rect[2:] for room in ROOMS}),10)
        self.assertGreater(len({len(room.blocks) for room in ROOMS}),3)
        for room in ROOMS:
            for block in room.blocks:
                self.assertGreater(block.w,0)
                self.assertGreater(block.h,0)
                self.assertGreaterEqual(block.x,0)
                self.assertGreaterEqual(block.y,0)
                self.assertLessEqual(block.x+block.w,room.rect[2])
                self.assertLessEqual(block.y+block.h,room.rect[3])

    def test_native_windows_do_not_cover_each_other(self):
        for seed in (0,1,42):
            tower = Tower((0,0,1600,900),seed)
            rects = list(tower.near(0).values())
            for i,(x,y,w,h) in enumerate(rects):
                for a,b,c,d in rects[i+1:]:
                    self.assertTrue(x+w<=a or a+c<=x or y+h<=b or b+d<=y)

    def test_revisiting_lower_sections_preserves_layout(self):
        tower = Tower((0,0,1600,900),42)
        original = tower.near(600)
        tower.near(-2000)
        self.assertEqual(original,tower.near(600))
        self.assertNotEqual(original,Tower(tower.bounds,43).near(600))

    def test_view_clips_native_windows_and_bounds_pool_size(self):
        for bounds in ((0,0,1600,900),(-1280,200,1280,720),(100,0,900,1600)):
            tower = Tower(bounds,17)
            ceiling=int(min(r[1] for r in tower.rectangles.values())-bounds[1]-bounds[3]/2)
            for offset in range(0,ceiling,-73):
                view = tower.view(offset)
                self.assertLessEqual(len(view),12)
                for rect,clip,full_height in view.values():
                    x,y,w,h = rect
                    self.assertGreaterEqual(x,bounds[0])
                    self.assertLessEqual(x+w,bounds[0]+bounds[2])
                    self.assertGreaterEqual(y,bounds[1]+28)
                    self.assertLessEqual(y+h,bounds[1]+bounds[3]-2)
                    self.assertGreaterEqual(clip,0)
                    self.assertLessEqual(h+clip,full_height)

    def test_five_stages_and_finite_summit(self):
        tower = Tower((0,0,1600,900),42)
        for stage in range(5):
            r = tower.rectangle(stage*3+1)
            self.assertEqual(tower.level_at(r[1]+r[3]/2),stage)
        self.assertEqual(tower.level_at(-1e6),4)
        self.assertIn(SUMMIT,ledges(tower.near(-1e6)))

    def test_full_climb_replays_from_each_actual_previous_landing(self):
        for width,height in ((1600,900),(900,1600)):
            for seed in (0,1,42):
                route = self.route if (width,height,seed)==(1600,900,42) else solve((0,0,width,height),seed)
                self.assertEqual(len(route),len(ROUTE)-1)
                self.assertEqual(route[0]['source'],START)
                self.assertEqual(route[-1]['target'],SUMMIT)
                for previous,current in zip(route,route[1:]):
                    self.assertEqual(previous['target'],current['source'])
                    self.assertAlmostEqual(previous['land_x'],current['start_x'])

    def test_opening_has_a_generous_charge_window(self):
        for jump in self.route[:7]:
            self.assertGreaterEqual(jump['tolerance'],5,jump)

    def test_opening_misses_remain_near_the_lesson(self):
        opening = [f for f in self.falls if int(f['source'].split(':')[0])<2]
        self.assertTrue(opening)
        self.assertLessEqual(max(f['drop'] for f in opening),360)
        first_room = [f for f in opening if f['source'].startswith('0:')]
        self.assertFalse(any(f['reset'] for f in first_room))

    def test_both_local_catches_and_long_falls_exist(self):
        local = [f for f in self.falls if f['landed'].split(':')[0]==f['source'].split(':')[0]]
        long = [f for f in self.falls if f['drop']>=720]
        self.assertGreater(len(local),len(self.falls)*.45)
        self.assertTrue(long)
        self.assertLess(len(long),len(self.falls)*.3)

    def test_long_fall_catches_have_a_route_back_to_the_climb(self):
        bounds=(0,0,1600,900)
        tower=Tower(bounds,42)
        platforms=ledges(tower.near(0))
        checked=set()
        for fall in self.falls:
            if fall['drop']<360 or fall['reset'] or fall['landed'] in checked:
                continue
            checked.add(fall['landed'])
            king=King(*bounds[2:])
            king.land(platforms[fall['landed']],fall['land_x'])
            # Recovery can cross a window seam, just like the authored climb.
            candidates=[key for key in ROUTE if key!=king.room
                        and abs(platforms[key].y-king.y)<220*king.scale]
            candidates.sort(key=lambda key:abs(platforms[key].y-king.y))
            direct=any(find_jump(king,key,platforms,bounds)[0] is not None
                       for key in candidates)
            if not direct and fall['landed'] in ('6:floor','12:floor'):
                # Both left basins need a connector around their solid divider.
                # Replay from the actual fall landing through the optional catch.
                recovery={'6:floor':('6:pan','6:beam'),
                          '12:floor':('12:catch','12:branch')}
                for target in recovery[fall['landed']]:
                    landed,witness=find_jump(king,target,platforms,bounds)
                    self.assertIsNotNone(landed,fall)
                    replay_step(king,witness,platforms,bounds)
                    self.assertEqual(king.room,target)
            else:
                self.assertTrue(direct,fall['landed'])
        self.assertGreater(len(checked),3)

    def test_first_crossing_catch_can_rejoin_the_opening(self):
        bounds=(0,0,1600,900)
        platforms=ledges(Tower(bounds,42).near(0))
        caught=[f for f in self.falls if f['source']=='0:monitor' and f['landed']=='1:floor']
        self.assertTrue(caught)
        for fall in caught:
            king=King(*bounds[2:])
            king.land(platforms['1:floor'],fall['land_x'])
            self.assertIsNotNone(find_jump(king,'0:monitor',platforms,bounds)[0])

    def test_shaft_supports_a_real_wall_rebound_route(self):
        diff_wall=[jump for jump in self.route if jump['source'].startswith('5:')
                and jump['target'].startswith('5:')]
        self.assertTrue(any(jump['bounced'] for jump in diff_wall))

    def test_revert_exit_has_a_clear_arc_from_supported_undo_positions(self):
        # The former 82px overhang rejected every direct jump with both feet
        # on UNDO. Its only solver witness depended on hanging off the left edge.
        # Keep the 96px rise and a deliberate charge, but test ordinary stances
        # with real inputs and reject head/side/screen rebounds along the arc.
        for width,height in ((1600,900),(2048,1152),(900,1600),(480,360)):
            for seed in (0,1,42):
                bounds=(0,0,width,height)
                platforms=ledges(Tower(bounds,seed).near(0))
                source=platforms['5:release'];target=platforms['5:exit']
                for fraction in (.27,1/3,.38):
                    wins=[]
                    for frames in range(1,37):
                        king=King(width,height)
                        king.land(source,source.left+(source.right-source.left)*fraction)
                        self.assertGreaterEqual(king.x-king.half,source.left)
                        self.assertLessEqual(king.x+king.half,source.right)
                        king.press()
                        for _ in range(frames):king.step(PROFILE.tick,platforms,0,bounds)
                        king.release(1)
                        for _ in range(120):
                            king.step(PROFILE.tick,platforms,0,bounds)
                            if king.room is not None or king.knocked:break
                        if king.room==target.key and not king.knocked:wins.append(frames)
                    self.assertGreaterEqual(len(wins),3,(bounds,seed,fraction,wins))
                    self.assertEqual(wins,list(range(min(wins),max(wins)+1)))
                    self.assertNotIn(36,wins,'Full charge should still overshoot this precision jump')

    def test_test_file_tabs_clear_both_supported_jump_setups(self):
        # Both old overhangs needed launches at/beyond the platform ends.
        # Test each rising arc, then replay the reversal from its actual landing.
        for width,height in ((1600,900),(2048,1152),(900,1600),(480,360)):
            for seed in (0,1,42):
                bounds=(0,0,width,height)
                platforms=ledges(Tower(bounds,seed).near(0))
                for source_key,target_key,direction,fractions in (
                    ('7:entry','7:fold',1,(.18,.24,.28)),
                    ('7:fold','7:exit',-1,(.54,.60,.68)),
                ):
                    source=platforms[source_key];target=platforms[target_key]
                    for fraction in fractions:
                        wins=[]
                        for frames in range(1,37):
                            king=King(width,height)
                            king.land(source,source.left+(source.right-source.left)*fraction)
                            self.assertGreaterEqual(king.x-king.half,source.left)
                            self.assertLessEqual(king.x+king.half,source.right)
                            king.press()
                            for _ in range(frames):king.step(PROFILE.tick,platforms,0,bounds)
                            king.release(direction)
                            for _ in range(120):
                                king.step(PROFILE.tick,platforms,0,bounds)
                                if king.room is not None or king.knocked:break
                            if king.room==target.key and not king.knocked:wins.append(frames)
                        self.assertGreaterEqual(len(wins),3,(bounds,seed,source_key,fraction,wins))
                        self.assertEqual(wins,list(range(min(wins),max(wins)+1)))
                        self.assertNotIn(36,wins)

                # No teleport or edge positioning between these two jumps.
                king=King(width,height);source=platforms['7:entry']
                king.land(source,source.left+(source.right-source.left)*.24)
                for target,direction in (('7:fold',1),('7:exit',-1)):
                    king.press()
                    for _ in range(26):king.step(PROFILE.tick,platforms,0,bounds)
                    king.release(direction)
                    for _ in range(120):
                        king.step(PROFILE.tick,platforms,0,bounds)
                        self.assertFalse(king.knocked,(bounds,seed,target))
                        if king.room is not None:break
                    self.assertEqual(king.room,target,(bounds,seed))

    def test_sleep_shelf_accepts_a_direct_jump_from_the_battery_middle(self):
        # Regression for a ledge whose underside forced an obscure rebound and
        # only two charge frames on wide monitors. No walking to an overhang.
        for width,height in ((1600,900),(1920,1080),(900,1600),(480,360)):
            for seed in (0,1,42):
                bounds=(0,0,width,height)
                platforms=ledges(Tower(bounds,seed).near(0))
                battery=platforms['9:bell'];shelf=platforms['9:rim']
                king=King(width,height)
                king.land(battery,(battery.left+battery.right)/2)
                wins=[]
                for frames in range(20,31):
                    result,bounced=launch(king,frames,-1,platforms,bounds,shelf.y)
                    if result.room==shelf.key and not bounced:wins.append(frames)
                self.assertGreaterEqual(len(wins),5,(bounds,seed,wins))
                self.assertEqual(wins,list(range(min(wins),max(wins)+1)))

    def test_late_night_shelf_has_direct_jumps_from_supported_standing_positions(self):
        # The old overhang defeated every left charge from ordinary positions.
        # Its solver witness walked beyond the visible shelf or used the screen
        # boundary. Check real charged input from several fully supported spots.
        for width,height in ((1600,900),(1920,1080),(2048,1152),(900,1600),(480,360)):
            for seed in (0,1,42):
                bounds=(0,0,width,height)
                platforms=ledges(Tower(bounds,seed).near(0))
                source=platforms['11:shelf'];target=platforms['11:exit']
                for fraction in (.35,.5,.65,.8):
                    wins=[]
                    for frames in range(18,31):
                        king=King(width,height)
                        king.land(source,source.left+(source.right-source.left)*fraction)
                        self.assertGreaterEqual(king.x-king.half,source.left)
                        self.assertLessEqual(king.x+king.half,source.right)
                        king.press()
                        for _ in range(frames):king.step(PROFILE.tick,platforms,0,bounds)
                        king.release(-1)
                        for _ in range(120):
                            king.step(PROFILE.tick,platforms,0,bounds)
                            if king.room is not None or king.knocked:break
                        if king.room==target.key and not king.knocked:wins.append(frames)
                    self.assertGreaterEqual(len(wins),5,(bounds,seed,fraction,wins))
                    self.assertEqual(wins,list(range(min(wins),max(wins)+1)))

    def test_opening_route_revisits_windows_at_new_heights(self):
        transfers=[(jump['source'].split(':')[0],jump['target'].split(':')[0])
                   for jump in self.route]
        self.assertIn(('1','0'),transfers)
        self.assertIn(('2','1'),transfers)

    def test_connected_terrain_hides_covered_top_edges(self):
        floor=(0,100,200,30)
        pier=(50,40,60,60)
        self.assertEqual(exposed_top(floor,[floor,pier]),[(0,50),(110,200)])
        self.assertEqual(exposed_top(pier,[floor,pier]),[(50,110)])


class CameraTests(unittest.TestCase):
    def test_camera_eases_both_up_and_down_without_changing_character(self):
        camera = Camera((0,0,1600,900))
        camera.step(1/60,100)
        self.assertLess(camera.offset,0)
        self.assertGreater(camera.offset,-200)
        for _ in range(180):
            camera.step(1/60,-700)
        high = camera.offset
        camera.step(1/60,-300)
        self.assertGreater(camera.offset,high)
        for _ in range(180):
            camera.step(1/60,800)
        self.assertAlmostEqual(camera.offset,0,places=5)

    def test_camera_stays_inside_starting_floor_and_keeps_falls_visible(self):
        camera = Camera((0,0,1600,900))
        camera.step(.016,800)
        self.assertEqual(camera.offset,0)
        camera.offset = -3000
        camera.step(.016,-2000)
        self.assertLessEqual(-2000-camera.offset,900*.88)


if __name__ == '__main__':
    unittest.main()
