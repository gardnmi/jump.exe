"""An original developer's five-year climb, told by one guide and physical objects."""
import random

from .course import ROOMS, SUMMIT, GUIDE_POINT, WHITE_PILL
from .life import DesktopLife
from .ending import Ending
from .atmosphere import Atmosphere

YEARS = ('YEAR 01', 'YEAR 02', 'YEAR 03', 'YEAR 04', 'YEAR 05')
GUIDE = (
    ("AI is writing code now.", "The white pill is up there, for anyone",
     "willing to learn and enjoy the ride."),
    ("The black pill stays down here.", "Take it, and everything new is a reason to quit.",
     "Comfortable seat. Terrible view."),
    ("Most of us take the long way.", "We deny it, rage at it, make our little deals...",
     "Then wonder what our hands are for."),
    ("Your keyboard isn't a relic.", "Let the machines help. Keep your judgment.",
     "There's still work worth making."),
)

# Objects are set on actual terrain surfaces, in the room's native coordinates.
# The same keyboard, chair and terminal recur in changing states over the years.
PROPS = (
    (('lamp','floor',.2,''), ('coffee','home',.8,''), ('books','loft',.84,'')),
    (),
    (('keyboard','base',.5,'manual'),),
    (('beacon','lip',.75,'error'),),
    (('vent','valve',.5,''), ('keyboard','tooth',.5,'broken'), ('coffee','floor',.2,'cold'),
     ('printer','floor',.62,'error')),
    (('bin','floor',.66,''),),
    (('keyboard','pan',.28,'manual'), ('notepad','pan',.76,'')),
    (('notepad','entry',.66,''),),
    (('books','floor',.12,''),),
    (),
    (('keyboard','entry',.7,'dust'),),
    (('lamp','entry',.25,''), ('chair','entry',.65,''), ('coffee','entry',.85,'cold'),
     ('notepad','shelf',.2,'')),
    (('keyboard','branch',.5,'manual'), ('cable','fork',.5,'joined'), ('plant','floor',.11,'')),
    (('plant','entry',.77,''),),
    (('keyboard','bank',.32,'manual'), ('coffee','entry',.4,''),
     ('plant','entry',.1,''), ('books','entry',.79,'')),
)


def objects(rank):
    blocks = {block.name:block for block in ROOMS[rank].blocks}
    return [(kind,blocks[anchor].x+blocks[anchor].w*fraction,blocks[anchor].y,value)
            for kind,anchor,fraction,value in PROPS[rank]]


def world_point(tower, rank, x, y):
    rx,ry,w,h = tower.rectangle(rank)
    rw,rh = ROOMS[rank].rect[2:]
    return rx+x*w/rw,ry+y*h/rh


class Story:
    def __init__(self):
        self.time = 0.
        self.page = 0
        self.guide_near = False
        self.accepted = False
        self.celebration = 0.
        self.particles = []
        self.last_room = None
        self.last_jumps = 0
        self.last_vx = 0.
        self.rng = random.Random(773)
        self.guide_point = (0.,0.)
        self.life = DesktopLife()
        self.atmosphere = Atmosphere()
        self.ending = Ending()
        self.play_seconds = 0.
        self.longest_fall = 0.
        self.air_high = None
        self.practice = False

    def talk(self):
        if self.guide_near:
            self.page = self.page+1 if self.page < len(GUIDE) else 0

    def summit_x(self,king,tower):
        x,_,w,_=tower.rectangle(14)
        return (king.x-x)*ROOMS[14].rect[2]/w

    def replay_ending(self,king,tower):
        self.ending.replay(self.summit_x(king,tower))

    def emit(self, x, y, scale, count=8, gold=False):
        for _ in range(count):
            self.particles.append([x,y,self.rng.uniform(-35,35)*scale,
                                   self.rng.uniform(-65,-15)*scale,
                                   self.rng.uniform(.22,.65),gold])
        self.particles = self.particles[-80:]

    def update(self, dt, king, tower, dev=False):
        self.time += dt
        self.ending.update(dt)
        if dev:
            self.practice = True
            self.air_high = None
        elif not self.accepted:
            self.play_seconds += dt
            if king.room is None:
                self.air_high = king.y if self.air_high is None else min(self.air_high,king.y)
            elif self.air_high is not None:
                self.longest_fall = max(self.longest_fall,(king.y-self.air_high)/king.scale)
                self.air_high = None
        self.celebration = max(0,self.celebration-dt)
        gx,gy = world_point(tower,*GUIDE_POINT)
        self.guide_point = gx,gy
        self.guide_near = (not dev and abs(king.x-gx)<110*king.scale
                           and abs(king.y-gy)<35*king.scale)
        self.life.update(dt,king,tower,landing=bool(king.room and self.last_room is None),
                         bounced=self.last_vx*king.vx<0 and king.impact>0)
        self.atmosphere.update(dt,king,tower,enabled=not dev and not self.ending.active)
        if not dev:
            if king.jumps > self.last_jumps:
                self.emit(king.x,king.y,king.scale)
            if king.room and self.last_room is None:
                self.emit(king.x,king.y,king.scale,12)
            if self.last_vx*king.vx<0 and king.impact>0:
                self.emit(king.x,king.y-king.body_height*.5,king.scale,5,True)
            px,py = world_point(tower,*WHITE_PILL)
            if not self.accepted and king.room == SUMMIT and abs(king.x-px)<23*king.scale:
                self.accepted = True
                self.ending.begin(self.play_seconds,king.jumps,self.longest_fall,self.practice,
                                  self.summit_x(king,tower))
                self.celebration = 5.
                self.emit(px,py-15*king.scale,king.scale,55,True)
        self.last_room,self.last_jumps,self.last_vx = king.room,king.jumps,king.vx
        for p in self.particles:
            p[0] += p[2]*dt
            p[1] += p[3]*dt
            p[3] += 150*king.scale*dt
            p[4] -= dt
        self.particles = [p for p in self.particles if p[4]>0]

    def state(self, camera_offset):
        return dict(scene_time=self.time,guide_near=self.guide_near,
                    guide_x=self.guide_point[0],guide_y=self.guide_point[1]-camera_offset,
                    dialogue=GUIDE[self.page] if self.guide_near and self.page<len(GUIDE) else [],
                    dialogue_page=self.page,accepted=self.accepted,celebration=self.celebration,
                    ending=self.ending.state(),
                    avatar_fx=dict(self.atmosphere.avatar),
                    encounters={str(rank):self.life.room(rank) for rank in range(len(ROOMS))},
                    particles=[(x,y-camera_offset,life,gold) for x,y,vx,vy,life,gold in self.particles])
