"""Jump King style physics in logical desktop coordinates; no GUI dependencies."""
from dataclasses import dataclass
import random
import math
from .physics_profile import PROFILE
from .course import ROOMS, START, SUMMIT, ROUTE, SPAWN_FRACTION
from .desktop_style import BG, ACCENTS


@dataclass(frozen=True)
class Ledge:
    key: str
    left: float
    right: float
    y: float
    depth: float = 20.


BODY_HALF = 10.
BODY_HEIGHT = 46.


def room_geometry(width, height, room_index):
    room = ROOMS[room_index]
    sx,sy = width/room.rect[2],height/room.rect[3]
    return [(block.name,(round(block.x*sx),round(block.y*sy),
                         round(block.w*sx),round(block.h*sy)),block.material)
            for block in room.blocks]


def exposed_top(rect, rectangles):
    """Visible top spans of a union of terrain rectangles, in local coordinates."""
    x,y,w,h = rect
    spans = [(x,x+w)]
    for other in rectangles:
        if other == rect:
            continue
        ox,oy,ow,oh = other
        if oy <= y <= oy+oh:
            cut = []
            for left,right in spans:
                if ox>left:
                    cut.append((left,min(right,ox)))
                if ox+ow<right:
                    cut.append((max(left,ox+ow),right))
            spans = [(a,b) for a,b in cut if b>a]
    return spans


def ledges(rectangles):
    result = {}
    for room,(x,y,w,h) in rectangles.items():
        for name,(px,py,pw,ph),material in room_geometry(w,h,int(room)):
            key = f'{room}:{name}'
            result[key] = Ledge(key,x+px,x+px+pw,y+py,ph)
    return result


def window_for(platform):
    return platform.split(':')[0] if platform is not None else None


THEMES = (
    ('DENIAL', BG, ACCENTS[0], .25),
    ('ANGER', BG, ACCENTS[1], .21),
    ('BARGAINING', BG, ACCENTS[2], .23),
    ('DEPRESSION', BG, ACCENTS[3], .20),
    ('ACCEPTANCE', BG, ACCENTS[4], .25),
)
ROOM_COUNT = len(ROOMS)
PLATFORM_COUNT = sum(len(room.blocks) for room in ROOMS)



class Tower:
    """An authored mountain split across differently sized native windows."""
    def __init__(self, bounds, seed):
        self.bounds,self.seed = bounds,seed
        self.scale = PROFILE.scale(*bounds[2:])
        self.base = bounds[1]+bounds[3]-315*self.scale
        left = bounds[0]+(bounds[2]-480*self.scale)/2
        self.rectangles = {}
        for index,room in enumerate(ROOMS):
            rng = random.Random(f'{seed}:{index}')
            x,y,w,h = room.rect
            # Tiny placement variation preserves authored lessons and fall corridors.
            dx,dy = rng.uniform(-2,2),rng.uniform(-2,2)
            self.rectangles[str(index)] = tuple(map(round,(
                left+(x+dx)*self.scale,self.base+(y+dy)*self.scale,
                w*self.scale,h*self.scale)))

    def rectangle(self, index):
        return self.rectangles[str(index)]

    def near(self, y):
        # All fifteen panes remain physical even through multi-room falls.
        return dict(self.rectangles)

    def level_at(self, y):
        index = min(range(ROOM_COUNT),key=lambda i: abs(
            self.rectangle(i)[1]+self.rectangle(i)[3]*.5-y))
        return index//3

    def view(self, offset):
        """Clip native windows to this monitor; retain full drawing origins."""
        left,top,width,height = self.bounds
        result = {}
        for role,(x,y,w,h) in self.rectangles.items():
            screen_y = round(y-offset)
            visible_top = max(round(top+28),screen_y)
            visible_bottom = min(round(top+height-2),screen_y+h)
            if visible_bottom-visible_top >= 3:
                result[role] = ((x,visible_top,w,visible_bottom-visible_top),
                                visible_top-screen_y,h)
        return result


class Camera:
    """A damped vertical dead zone, following both ascents and long falls."""
    def __init__(self, bounds):
        self.bounds = bounds
        self.offset = 0.

    def step(self, dt, world_y):
        top, height = self.bounds[1], self.bounds[3]
        screen_y = world_y-self.offset
        target = self.offset
        if screen_y < top+height*.38:
            target = world_y-top-height*.38
        elif screen_y > top+height*.68:
            target = world_y-top-height*.68
        target = min(0.,target)
        self.offset += (target-self.offset)*(1-math.exp(-10*max(0,dt)))
        # During very long falls keep the knight inside the viewport.
        self.offset = min(0.,max(world_y-top-height*.88,
                                min(world_y-top-height*.12,self.offset)))


def swept_contact(ox, oy, nx, ny, platform, half=BODY_HALF, body_height=BODY_HEIGHT):
    """Sweep the knight's body against a solid ledge, including sides/underside."""
    enter, leave = -math.inf, math.inf
    normal = (0,0)
    for start,delta,lo,hi,axis in (
        (ox,nx-ox,platform.left-half,platform.right+half,0),
        (oy,ny-oy,platform.y,platform.y+platform.depth+body_height,1),
    ):
        if abs(delta)<1e-10:
            if start < lo or start > hi:
                return None
            continue
        a,b = (lo-start)/delta,(hi-start)/delta
        sign = -1 if delta>0 else 1
        if a>b:
            a,b = b,a
        if a>enter:
            enter = a
            normal = (sign,0) if axis == 0 else (0,sign)
        leave = min(leave,b)
        if enter>leave:
            return None
    if enter < -1e-9 or enter > 1 or leave < 0:
        return None
    return max(0.,enter),normal


class King:
    def __init__(self, width=1600, height=900):
        self.width, self.height = width, height
        self.scale = PROFILE.scale(width,height)
        self.half = PROFILE.body_width*self.scale/2
        self.body_height = PROFILE.body_height*self.scale
        self.gravity = PROFILE.gravity*self.scale
        self.accumulator = 0.
        self.jump_held = False
        self.recovery = 0.
        self.impact = 0.
        self.knocked = False
        self.x = self.y = self.vx = self.vy = 0.
        self.room = None
        self.local = 0.
        self.charge = 0.
        self.charging = False
        self.walk_phase = 0.
        self.walking = False
        self.facing = 1
        self.jumps = self.falls = 0
        self.visited = set()
        self.trail = []

    def reset(self, platforms):
        self.__init__(self.width, self.height)
        self.enter(platforms)

    def enter(self, platforms):
        self.cancel()
        self.trail.clear()
        start = platforms.get(START) or max(platforms.values(), key=lambda p: (p.y, -p.left))
        fraction = SPAWN_FRACTION if start.key == START else .5
        self.land(start, start.left + (start.right - start.left) * fraction)

    def land(self, platform, x):
        if self.vy > PROFILE.heavy_landing_speed*self.scale:
            self.recovery = PROFILE.heavy_landing_seconds
        self.knocked = False
        self.room = platform.key
        self.x, self.y = x, platform.y
        self.local = x - platform.left
        self.vx = self.vy = 0.
        self.visited.add(platform.key)

    def press(self):
        self.jump_held = True
        if self.room is not None and not self.charging and self.recovery <= 0:
            self.charging = True
            self.charge = 0.

    def cancel(self):
        self.jump_held = False
        self.charging = False
        self.charge = 0.

    def release(self, direction):
        self.jump_held = False
        if not self.charging or self.room is None:
            return
        frames = max(1,min(PROFILE.charge_frames,round(self.charge*PROFILE.charge_frames)))
        power = (frames-1)/(PROFILE.charge_frames-1)
        self.vy = -(PROFILE.jump_y_min+(PROFILE.jump_y_max-PROFILE.jump_y_min)*power)*self.scale
        self.vx = direction*(PROFILE.jump_x_min+(PROFILE.jump_x_max-PROFILE.jump_x_min)*power)*self.scale
        if direction:
            self.facing = direction
        self.room = None
        self.charging = False
        self.charge = 0.
        self.jumps += 1

    @property
    def pose(self):
        if self.recovery > 0:
            return 'land'
        if self.knocked:
            return 'bonk'
        if self.charging:
            return 'charge'
        if self.room is None:
            return 'rise' if self.vy < 0 else 'fall'
        return 'walk' if self.walking else 'idle'

    def step(self, dt, platforms, direction, bounds):
        self.accumulator += max(0.,min(dt,.1))
        while self.accumulator+1e-9 >= PROFILE.tick:
            self.accumulator -= PROFILE.tick
            self._frame(PROFILE.tick,platforms,direction,bounds)

    def _frame(self, dt, platforms, direction, bounds):
        self.recovery = max(0.,self.recovery-dt)
        self.impact = max(0.,self.impact-dt)
        left, top, width, height = bounds
        self.walking = False
        if direction and self.room is not None:
            self.facing = direction
        if self.room in platforms:
            p = platforms[self.room]
            self.x, self.y = p.left + self.local, p.y
            if self.jump_held and not self.charging and self.recovery <= 0:
                self.press()
            if self.charging:
                self.charge = min(PROFILE.charge_frames,
                                  round(self.charge*PROFILE.charge_frames)+1)/PROFILE.charge_frames
            elif self.recovery <= 0:
                self.walking = bool(direction)
                self.walk_phase += dt*12 if direction else 0
                desired_x = self.x+direction*PROFILE.walk_speed*self.scale*dt
                blocks = []
                for other in platforms.values():
                    if other.key == p.key or not other.y < self.y < other.y+other.depth+self.body_height:
                        continue
                    hit = swept_contact(self.x,self.y,desired_x,self.y,other,self.half,self.body_height)
                    if hit is not None:
                        blocks.append(hit[0])
                if blocks:
                    desired_x = self.x+(desired_x-self.x)*min(blocks)-direction*.01
                self.x = desired_x
                self.local = self.x-p.left
            if not p.left-self.half <= self.x <= p.right+self.half:
                self.room = None
                self.cancel()
                self.vx = direction*PROFILE.walk_speed*self.scale
        elif self.room is not None:
            self.room = None
            self.cancel()
        if self.room is None:
            # Small substeps and segment/ledge intersections prevent tunnelling.
            remaining = dt
            while remaining > 1e-9 and self.room is None:
                step = min(remaining, 1/240)
                remaining -= step
                ox, oy = self.x, self.y
                self.vy = min(PROFILE.terminal_speed*self.scale,self.vy+self.gravity*step)
                nx, ny = ox + self.vx * step, oy + self.vy * step
                hits = []
                for p in platforms.values():
                    if (max(ox,nx)+self.half < p.left or min(ox,nx)-self.half > p.right
                            or max(oy,ny) < p.y or min(oy,ny)-self.body_height > p.y+p.depth):
                        continue
                    contact = swept_contact(ox,oy,nx,ny,p,self.half,self.body_height)
                    if contact is not None:
                        t,normal = contact
                        hits.append((t,p.key,normal))
                if hits:
                    t,key,(normal_x,normal_y) = min(hits)
                    p = platforms[key]
                    self.x,self.y = ox+(nx-ox)*t,oy+(ny-oy)*t
                    if normal_y == -1:
                        self.land(p,self.x)
                    elif normal_y == 1:
                        self.y = p.y+p.depth+self.body_height+.01
                        self.vy = abs(self.vy)*PROFILE.head_restitution
                        self.knocked = True
                        self.impact = .12
                    else:
                        self.x = p.left-self.half-.01 if normal_x<0 else p.right+self.half+.01
                        self.vx = -self.vx*PROFILE.wall_restitution
                        self.knocked = True
                        self.impact = .12
                else:
                    self.x, self.y = nx, ny
                if self.x < left+self.half or self.x > left+width-self.half:
                    self.x = max(left+self.half,min(left+width-self.half,self.x))
                    self.vx *= -PROFILE.wall_restitution
                    self.knocked = True
                    self.impact = .12
                if self.y > top+height+70:
                    start = platforms.get(START) or max(platforms.values(), key=lambda p: (p.y, -p.left))
                    self.falls += 1
                    fraction = SPAWN_FRACTION if start.key == START else .5
                    self.land(start, start.left+(start.right-start.left)*fraction)
                    self.cancel()
        self.trail.append((self.x, self.y-18))
        self.trail = self.trail[-12:]
