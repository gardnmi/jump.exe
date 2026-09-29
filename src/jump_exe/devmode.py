"""Free flight and repeatable practice placements, independent of the GUI."""
import math

from .course import ROOMS


class DevMode:
    def __init__(self, active=False):
        self.active = active
        self.checkpoint = None
        self.selected_room = None

    @staticmethod
    def clear_motion(king):
        king.cancel()
        king.vx = king.vy = king.accumulator = 0.
        king.recovery = king.impact = king.walk_phase = 0.
        king.walking = king.knocked = False
        king.room = None
        king.local = 0.
        king.trail.clear()

    @staticmethod
    def clear_at(king, platforms, x=None, y=None):
        x = king.x if x is None else x
        y = king.y if y is None else y
        return not any(
            x+king.half > p.left+1e-6 and x-king.half < p.right-1e-6
            and y > p.y+1e-6 and y-king.body_height < p.y+p.depth-1e-6
            for p in platforms.values())

    def enter(self, king):
        self.selected_room = int(king.room.split(':')[0]) if king.room else None
        self.clear_motion(king)
        self.active = True

    def place(self, king, platforms, point):
        x,y,facing = point
        if not self.clear_at(king,platforms,x,y):
            return False
        self.clear_motion(king)
        king.x,king.y,king.facing = x,y,facing
        for p in platforms.values():
            if abs(y-p.y) < .01 and p.left-king.half < x < p.right+king.half:
                king.land(p,x)
                break
        return True

    def resume(self, king, platforms):
        point = king.x,king.y,king.facing
        if not self.place(king,platforms,point):
            return False
        self.checkpoint = point
        self.active = False
        return True

    def retry(self, king, platforms):
        if self.checkpoint is None or not self.place(king,platforms,self.checkpoint):
            return False
        self.active = False
        return True

    def room_index(self, king, tower):
        if self.selected_room is not None:
            return self.selected_room
        return min(range(len(ROOMS)),key=lambda i: abs(
            tower.rectangle(i)[1]+tower.rectangle(i)[3]*.5-king.y))

    def skip_room(self, king, platforms, tower, direction):
        index = max(0,min(len(ROOMS)-1,self.room_index(king,tower)+direction))
        p = platforms[f'{index}:{ROOMS[index].route[0]}']
        center = (p.left+p.right)/2
        # A broad floor may have cliffs on top of it; choose a clear standing span.
        candidates = [center,p.left+king.half,p.right-king.half]
        for other in platforms.values():
            candidates.extend((other.left-king.half-.01,other.right+king.half+.01))
        for x in sorted(candidates,key=lambda x: abs(x-center)):
            if (p.left+king.half <= x <= p.right-king.half
                    and self.clear_at(king,platforms,x,p.y)):
                self.clear_motion(king)
                king.x,king.y = x,p.y
                self.selected_room = index
                return True
        return False

    def move(self, king, dt, keys, tower):
        dx = int(bool(keys & {'d','right'}))-int(bool(keys & {'a','left'}))
        dy = int(bool(keys & {'s','down'}))-int(bool(keys & {'w','up'}))
        if not (dx or dy):
            return
        self.selected_room = None
        speed = 180*king.scale
        if keys & {'shift_l','shift_r'}:
            speed *= 4
        if keys & {'control_l','control_r'}:
            speed *= .25
        step = speed*max(0,min(.05,dt))/math.hypot(dx,dy)
        left,top,width,height = tower.bounds
        king.x = max(left+king.half,min(left+width-king.half,king.x+dx*step))
        ceiling = min(r[1] for r in tower.rectangles.values())-king.body_height*2
        king.y = max(ceiling,min(top+height+50,king.y+dy*step))
        if dx:
            king.facing = dx
