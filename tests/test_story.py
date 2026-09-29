import unittest
from jump_exe.course import SUMMIT, ROOMS, WHITE_PILL
from jump_exe.model import King, Tower, ledges
from jump_exe.story import Story, GUIDE, objects, world_point


class StoryTests(unittest.TestCase):
    def setUp(self):
        self.tower=Tower((0,0,1600,900),42)
        self.platforms=ledges(self.tower.near(0))
        self.king=King(1600,900)
        self.king.enter(self.platforms)
        self.story=Story()

    def test_starting_caretaker_introduces_the_pill_goal(self):
        self.story.update(0,self.king,self.tower)
        self.assertTrue(self.story.guide_near)
        self.assertIn('white pill',' '.join(self.story.state(0)['dialogue']))
        for _ in GUIDE:self.story.talk()
        self.assertEqual(self.story.state(0)['dialogue'],[])
        self.story.talk()
        self.assertEqual(self.story.page,0)

    def test_later_story_does_not_interrupt_the_climb_with_dialogue(self):
        self.story.update(0,self.king,self.tower)
        self.story.talk()
        self.king.land(self.platforms['4:entry'],self.platforms['4:entry'].left+50)
        self.story.update(.1,self.king,self.tower)
        self.assertFalse(self.story.guide_near)
        self.assertEqual(self.story.state(0)['dialogue'],[])
        self.story.talk()
        self.assertEqual(self.story.page,1)

    def test_collect_white_pill_only_when_reaching_it_on_summit(self):
        p=self.platforms[SUMMIT]
        self.king.land(p,p.right-10*self.king.scale)
        self.story.update(.1,self.king,self.tower)
        self.assertFalse(self.story.accepted)
        x,_=world_point(self.tower,*WHITE_PILL)
        self.king.land(p,x)
        self.story.update(.1,self.king,self.tower)
        self.assertTrue(self.story.accepted)
        self.assertGreater(self.story.celebration,0)
        self.assertGreater(len(self.story.particles),40)
        self.king.room=None
        self.king.y+=100
        self.story.update(.1,self.king,self.tower)
        self.assertTrue(self.story.accepted)

    def test_dev_flight_does_not_trigger_dialogue_or_collect_pill(self):
        self.story.update(.1,self.king,self.tower,dev=True)
        self.assertFalse(self.story.guide_near)
        x,_=world_point(self.tower,*WHITE_PILL)
        self.king.land(self.platforms[SUMMIT],x)
        self.story.update(.1,self.king,self.tower,dev=True)
        self.assertFalse(self.story.accepted)
        self.story.update(.1,self.king,self.tower)
        self.assertTrue(self.story.accepted)

    def test_story_and_effects_do_not_move_the_player(self):
        self.king.press();self.king.release(1)
        before=vars(self.king).copy()
        self.story.update(.1,self.king,self.tower)
        self.assertEqual(vars(self.king),before)
        self.assertTrue(self.story.particles)
        self.story.update(2,self.king,self.tower)
        self.assertFalse(self.story.particles)

    def test_props_follow_real_terrain_and_stay_in_their_room(self):
        for rank,room in enumerate(ROOMS):
            for kind,x,y,value in objects(rank):
                self.assertGreaterEqual(x,0,(rank,kind))
                self.assertLessEqual(x,room.rect[2],(rank,kind))
                self.assertTrue(any(b.y==y and b.x<=x<=b.x+b.w for b in room.blocks))


if __name__=='__main__':
    unittest.main()
