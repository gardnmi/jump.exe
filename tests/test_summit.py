import unittest

from jump_exe.course import ROOMS
from jump_exe.model import King, Tower, ledges, exposed_top
from jump_exe.physics_profile import PROFILE
from jump_exe.routecheck import launch, find_jump, replay_step
from jump_exe.shortcutcheck import scan_source


class SummitTests(unittest.TestCase):
    def test_left_workstation_catch_rejoins_the_route_after_a_long_fall(self):
        for bounds in ((0,0,1600,900),(0,0,900,1600)):
            for seed in (0,1,42):
                tower=Tower(bounds,seed);p=ledges(tower.near(0))
                king=King(*bounds[2:])
                king.land(p['12:floor'],p['12:floor'].left+18*tower.scale)
                for target in ('12:catch','12:branch'):
                    landed,witness=find_jump(king,target,p,bounds)
                    self.assertIsNotNone(landed,(bounds,seed,target))
                    replay_step(king,witness,p,bounds)
                    self.assertEqual(king.room,target)

    def test_bank_has_a_small_repeatable_charge_window_from_supported_feet(self):
        for bounds in ((0,0,480,360),(0,0,1600,900),
                       (0,0,2048,1152),(100,0,900,1600)):
            for seed in (0,1,42):
                p=ledges(Tower(bounds,seed).near(0))
                source,target=p['14:bridge'],p['14:bank']
                king=King(*bounds[2:])
                king.land(source,source.left+(source.right-source.left)*.75)
                self.assertGreaterEqual(king.x-king.half,source.left)
                self.assertLessEqual(king.x+king.half,source.right)
                good=[]
                for frames in range(1,PROFILE.charge_frames+1):
                    landed,bounced=launch(king,frames,1,p,bounds,target.y)
                    if landed.room==target.key:
                        self.assertTrue(bounced)
                        good.append(frames)
                self.assertGreaterEqual(len(good),3,(bounds,seed,good))
                self.assertLessEqual(len(good),4,(bounds,seed,good))
                self.assertEqual(good,list(range(good[0],good[-1]+1)))
                self.assertNotIn(PROFILE.charge_frames,good)

    def test_case_cannot_be_used_as_a_ladder_around_the_upper_keys(self):
        blocks={b.name:b for b in ROOMS[14].blocks}
        rects=[(b.x,b.y,b.w,b.h) for b in blocks.values()]
        for name in ('tower','hood','foot'):
            b=blocks[name]
            self.assertEqual(exposed_top((b.x,b.y,b.w,b.h),rects),[],name)
        # Includes body overhang, every charge and both directions/vertical jumps.
        # The collision search complements the height bounds in test_shortcuts.
        for bounds,seed in (((0,0,1600,900),42),((0,0,900,1600),1)):
            for source,forbidden in (
                ('bridge',('release','summit','tower','hood')),
                ('bank',('summit','tower','hood')),
            ):
                _,edges=scan_source(('14:'+source,bounds,seed,4))
                for target in forbidden:
                    self.assertNotIn('14:'+target,edges,(bounds,source,target))


if __name__=='__main__':unittest.main()
