import unittest
from jump_exe.model import King,Tower,ledges
from jump_exe.physics_profile import PROFILE
from jump_exe.routecheck import launch
from jump_exe.shortcutcheck import handoff_violations,within_jump_envelope,scan_source


class ShortcutTests(unittest.TestCase):
    def test_every_later_window_requires_the_previous_departure(self):
        # Includes floors, connector stubs and decorative-looking casing tops,
        # not just the platforms listed in the walkthrough. This analytic bound
        # covers launch positions between the simulation's sampled positions.
        for bounds in ((0,0,480,360),(0,0,1600,900),(0,0,2048,1152),
                       (100,0,900,1600),(-1280,200,1280,720)):
            for seed in range(50):
                self.assertEqual(handoff_violations(bounds,seed),[],(bounds,seed))

    def test_key_internal_sequences_cannot_be_cleared_in_one_jump(self):
        p=ledges(Tower((0,0,480,360),42).near(0))
        for source,target in (('4:floor','4:valve'),('4:entry','4:rim'),
                              ('7:entry','7:exit'),
                              ('8:floor','8:hinge'),('10:entry','10:undo'),
                              ('12:fork','12:exit'),('13:entry','13:exit'),('14:entry','14:bridge'),
                              ('14:landing','14:bank'),('14:bridge','14:release'),
                              ('14:bank','14:summit'),('12:catch','12:exit')):
            self.assertFalse(within_jump_envelope(p[source],p[target],1),(source,target))

    def test_review_divider_forces_the_left_crossing(self):
        # Height alone would permit some of these jumps. Actual solid sides and
        # undersides must close the old right-side ladder, including banks.
        for source in ('8:floor','8:entry','8:latch'):
            _,edges=scan_source((source,(0,0,1600,900),42,4))
            for target in ('8:cap','8:hinge','8:exit','8:mullion'):
                self.assertNotIn(target,edges,(source,target))

    def test_ci_precision_platform_and_return_allow_fully_supported_takeoffs(self):
        for bounds in ((0,0,480,360),(0,0,1600,900),
                       (0,0,2048,1152),(100,0,900,1600)):
            for seed in (0,1,42):
                tower=Tower(bounds,seed);p=ledges(tower.near(0))
                for source,target,direction,fractions in (
                    ('13:entry','13:bridge',1,(.15,.18,.2)),
                    ('13:bridge','13:exit',-1,(.5,.55)),
                    ('13:exit','14:entry',-1,(.85,)),
                ):
                    for fraction in fractions:
                        start,end=p[source],p[target]
                        k=King(*bounds[2:])
                        k.land(start,start.left+(start.right-start.left)*fraction)
                        self.assertGreaterEqual(k.x-k.half,start.left)
                        self.assertLessEqual(k.x+k.half,start.right)
                        successes=[]
                        for frames in range(1,PROFILE.charge_frames+1):
                            result,bounced=launch(k,frames,direction,p,bounds,end.y)
                            if result.room==target and not bounced:successes.append(frames)
                        self.assertGreaterEqual(len(successes),3,(bounds,seed,source,fraction,successes))
                        self.assertEqual(successes,list(range(successes[0],successes[-1]+1)))
                        if target!='14:entry':self.assertNotIn(PROFILE.charge_frames,successes)


if __name__=='__main__':unittest.main()
