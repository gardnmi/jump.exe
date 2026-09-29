import copy
import unittest
from jump_exe.life import DesktopLife
from jump_exe.model import King,Tower,ledges


class DesktopLifeTests(unittest.TestCase):
    def setUp(self):
        self.tower=Tower((0,0,1600,900),42)
        self.platforms=ledges(self.tower.near(0))
        self.king=King(1600,900)
        self.king.enter(self.platforms)
        self.life=DesktopLife()

    def go(self,key,fraction=.5):
        p=self.platforms[key]
        self.king.land(p,p.left+(p.right-p.left)*fraction)

    def advance(self,seconds):
        for _ in range(round(seconds*60)):self.life.update(1/60,self.king,self.tower)

    def test_duck_perches_then_flees_when_approached(self):
        self.life.update(.01,self.king,self.tower)
        self.assertTrue(self.life.room(0)[0]['perched'])
        self.assertEqual(self.life.room(0)[0]['visits'],0)
        self.go('0:home',.1)
        self.life.update(.01,self.king,self.tower)
        duck=self.life.room(0)[0]
        self.assertTrue(duck['active'])
        self.assertFalse(duck['perched'])
        self.assertEqual(duck['direction'],1)

    def test_encounter_waits_for_distance_and_cooldown_before_rearming(self):
        self.go('0:home',.1)
        self.advance(15)
        self.assertEqual(self.life.room(0)[0]['visits'],1)
        self.assertFalse(self.life.room(0)[0]['perched'])
        self.go('14:summit')
        self.advance(.1)
        self.assertTrue(self.life.room(0)[0]['perched'])
        self.go('0:home',.1)
        self.advance(.1)
        self.assertEqual(self.life.room(0)[0]['visits'],2)

    def test_hardware_and_diff_events_require_their_specific_impact(self):
        self.go('4:valve')
        self.life.update(.01,self.king,self.tower)
        self.assertFalse(self.life.room(4)[0]['active'])
        self.life.update(.01,self.king,self.tower,landing=True)
        self.advance(.5)
        self.assertGreater(self.life.room(4)[0]['spin'],0)
        self.go('5:release')
        self.life.update(.01,self.king,self.tower,landing=True)
        self.assertFalse(self.life.room(5)[0]['active'])
        self.life.update(.01,self.king,self.tower,bounced=True)
        self.assertTrue(self.life.room(5)[0]['active'])

    def test_events_are_cosmetic_and_restart_cleanly(self):
        self.go('12:branch',.25)
        before=copy.deepcopy(vars(self.king))
        self.advance(.5)
        self.assertEqual(vars(self.king),before)
        self.assertTrue(self.life.room(12)[0]['active'])
        fresh=DesktopLife()
        self.assertEqual(fresh.room(12)[0]['visits'],0)
        self.assertFalse(fresh.room(12)[0]['active'])

    def test_new_desk_encounters_react_in_their_own_rooms(self):
        for rank,anchor,kind in ((0,'loft','ghost'),(11,'shelf','cat'),(12,'fork','bot')):
            with self.subTest(kind=kind):
                self.life=DesktopLife()
                self.go(f'{rank}:{anchor}',.75)
                self.advance(.1)
                event=next(e for e in self.life.room(rank) if e['kind']==kind)
                self.assertTrue(event['active'])
                self.assertEqual(event['visits'],1)


if __name__=='__main__':
    unittest.main()
