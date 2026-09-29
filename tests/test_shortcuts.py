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
                              ('12:fork','12:exit'),('14:entry','14:bridge'),
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

    def test_ci_exit_has_an_intentional_bank_off_visible_hardware(self):
        bounds=(0,0,1600,900);tower=Tower(bounds,42);p=ledges(tower.near(0))
        source=p['13:bridge'];rail=p['13:rail']
        successes=[]
        for frames in range(25,37):
            k=King(*bounds[2:]);k.land(source,rail.left-18*tower.scale)
            result,bounced=launch(k,frames,1,p,bounds,p['13:exit'].y)
            if result.room=='13:exit' and bounced:successes.append(frames)
        self.assertGreaterEqual(len(successes),3,successes)


if __name__=='__main__':unittest.main()
