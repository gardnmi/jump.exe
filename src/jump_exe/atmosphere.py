"""Read-only reactions to the player, in each window's native pixel coordinates."""
from collections import deque
import math
import random

from .course import ROOMS
from .desktop_style import JADE, RED, YELLOW, BLUE, CYAN


# Recessed display glass already present in the room artwork.
SCREENS = (
    (12,103,215,120),(14,69,88,40),(56,116,110,120),
    (10,40,121,28),(40,124,184,190),(32,76,63,90),
    (67,46,151,84),(8,78,114,74),(12,88,242,170),
    (8,75,80,64),(75,80,138,80),(12,77,116,120),
    (155,65,129,230),(10,78,113,40),(147,332,110,151),
)
RESIDENTS = (0,2,4,11,12,14)
COLORS = (JADE,RED,YELLOW,BLUE,CYAN)


def pulse(age, duration):
    return max(0.,math.sin(math.pi*age/duration)) if 0 <= age < duration else 0.


def vent_point(rank):
    block = next(b for b in ROOMS[rank].blocks if b.name == ROOMS[rank].route[0])
    return block.x+min(18,block.w/2),block.y-6


class Atmosphere:
    def __init__(self):
        self.time = 0.
        self.enabled = True
        self.rng = random.Random(941)
        self.rooms = [dict(wake=-100.,vent=-100.,arc=-100.,scan=-100.,
                           build=-100.,shake=-100.,moth=-100.,entered=-100.,
                           near=False,moth_near=False,particles=[],echo=None,
                           reflection=None,hero=None,vent_origin=vent_point(rank))
                      for rank in range(len(ROOMS))]
        self.history = deque(maxlen=32)
        self.last_sample = -1.
        self.previous = None
        self.neighbor_at = -100.
        self.neighbor_count = 0
        self.settle_at = -100.
        self.avatar = {}

    def spawn(self, rank, kind, x, y, count, drift=0., strength=1.):
        state = self.rooms[rank]
        for _ in range(count):
            state['particles'].append(dict(
                kind=kind,x=x+self.rng.uniform(-7,7),y=y-self.rng.uniform(1,8),
                vx=drift*.28+self.rng.uniform(-25,25)*strength,
                vy=-self.rng.uniform(16,42)*strength,
                life=self.rng.uniform(1.2,2.2) if kind!='paper' else 4.,
                settled=False,glyph=self.rng.choice(('{}',';', '//','?'))))
        del state['particles'][:-48]

    def advance_particles(self, rank, dt):
        state=self.rooms[rank]
        for p in state['particles']:
            p['life']-=dt
            if p['settled']:continue
            old_y=p['y']
            p['x']+=p['vx']*dt
            p['vy']+=(58 if p['kind'] in ('paper','text') else -7 if p['kind']=='check' else 100)*dt
            p['y']+=p['vy']*dt
            if p['vy']>0 and p['kind'] in ('paper','screw','dust'):
                surfaces=[b for b in ROOMS[rank].blocks
                          if b.x<=p['x']<=b.x+b.w and old_y<=b.y-1<=p['y']]
                if surfaces:
                    p['y']=min(b.y for b in surfaces)-1
                    p['settled']=True
                    p['life']=min(p['life'],1.3 if p['kind']=='paper' else .45)
        w,h=ROOMS[rank].rect[2:]
        state['particles']=[p for p in state['particles']
                            if p['life']>0 and -12<p['x']<w+12 and -16<p['y']<h+12]

    def update(self, dt, king, tower, enabled=True):
        dt=max(0.,min(dt,.1))
        sample=dict(x=king.x,y=king.y,vx=king.vx,vy=king.vy,room=king.room,
                    jumps=king.jumps,facing=king.facing,pose=king.pose)
        self.enabled=enabled
        if not enabled:
            self.previous=sample
            self.avatar={}
            self.history.clear()
            self.settle_at=-100.
            for state in self.rooms:
                state.update(hero=None,reflection=None,echo=None,near=False,moth_near=False)
                for key in ('wake','vent','arc','scan','build','shake','moth','entered'):
                    state[key]=-100.
                state['particles'].clear()
            return
        self.time+=dt
        prev=self.previous or sample
        landing=king.room is not None and prev['room'] is None
        jumped=king.jumps>prev['jumps']
        for rank,state in enumerate(self.rooms):
            self.advance_particles(rank,dt)
            state['hero']=state['reflection']=None
            if state['echo'] and self.time-state['echo']['start']>1.2:state['echo']=None
        rectangles=tower.near(king.y)
        def distance(item):
            _,(x,y,w,h)=item
            return math.hypot(max(x-king.x,0,king.x-x-w),
                              max(y-king.y+14*king.scale,0,king.y-14*king.scale-y-h))
        role,rectangle=min(rectangles.items(),key=distance)
        if king.room is not None:
            role=king.room.split(':')[0];rectangle=rectangles[role]
        rank=int(role);stage=rank//3;state=self.rooms[rank]
        rx,ry,rw,rh=rectangle;w,h=ROOMS[rank].rect[2:]
        px=(king.x-rx)*w/rw;py=(king.y-ry)*h/rh
        near=distance((role,rectangle))<35*king.scale
        hero=dict(x=px,y=py,facing=king.facing,pose=king.pose)
        for i,other in enumerate(self.rooms):
            if i!=rank:other['near']=other['moth_near']=False
        if near:
            state['hero']=hero
            if not state['near'] and self.time-state['entered']>8:
                state['wake']=state['entered']=self.time
                if stage==2:state['scan']=self.time
            if stage==1 and self.time-state['vent']>7:
                state['vent']=self.time
                block=min(ROOMS[rank].blocks,key=lambda b:abs(b.y-py)+max(b.x-px,0,px-b.x-b.w))
                vx,vy=block.x+min(18,block.w/2),block.y-6
                state['vent_origin']=(vx,vy)
                self.spawn(rank,'paper',vx,vy,5,100)
            if stage==1 and self.time-state['arc']>5.5:
                state['arc']=self.time
            if stage==2 and self.time-state['scan']>10:state['scan']=self.time
            if stage==4 and self.time-state['build']>12:state['build']=self.time
            sx,sy,sw,sh=SCREENS[rank]
            moth_near=math.hypot(px-(sx+sw-8),py-(sy+sh))<45
            if moth_near and not state['moth_near'] and self.time-state['moth']>6:
                state['moth']=self.time
            state['moth_near']=moth_near
            if self.time-self.neighbor_at>14:
                neighbor=rank+(1 if self.neighbor_count%2==0 else -1)
                if 0<=neighbor<len(ROOMS):self.rooms[neighbor]['wake']=self.time
                self.neighbor_at=self.time;self.neighbor_count+=1
        else:state['moth_near']=False
        state['near']=near
        if jumped and near:
            if stage==0:
                state['echo']=dict(start=self.time,x=px,y=py,facing=king.facing,
                                   direction=-king.facing,pose='rise')
            elif stage==2:
                self.spawn(rank,'paper',px,py-10,4,king.vx/king.scale)
        if landing:
            rank=int(king.room.split(':')[0]);stage=rank//3;state=self.rooms[rank]
            rx,ry,rw,rh=rectangles[str(rank)];w,h=ROOMS[rank].rect[2:]
            px=(king.x-rx)*w/rw;py=(king.y-ry)*h/rh
            drift=prev['vx']/king.scale
            hard=prev['vy']/king.scale>610 or king.recovery>0
            self.spawn(rank,'dust',px,py,16 if stage==3 else 10 if hard else 5,
                       drift,1.3 if hard else .8)
            if hard:
                self.settle_at=self.time
                state['shake']=self.time
            if stage==0:
                for echo_state in self.rooms[:3]:
                    if echo_state['echo']:
                        echo_state['echo']=None
                self.spawn(rank,'text',px,py-16,9,drift)
            elif stage==1:
                state['arc']=self.time
                if hard:self.spawn(rank,'screw',px,py,7,drift,1.5)
            elif stage==2:self.spawn(rank,'paper',px,py-3,5,drift)
            elif stage==4:
                state['build']=self.time
                self.spawn(rank,'check',px,py-7,6,drift)
                for adjacent in (rank-1,rank+1):
                    if 12<=adjacent<15:self.rooms[adjacent]['wake']=self.time
        if self.time-self.last_sample>=.06:
            self.history.append((self.time,int(role),hero))
            self.last_sample=self.time
        if stage==3 and near:
            old=next((pose for time,r,pose in reversed(self.history)
                      if r==rank and self.time-time>=.22),None)
            state['reflection']=dict(old) if old else None
        self.avatar={}
        if near:
            sx,sy,sw,sh=SCREENS[rank]
            screen_distance=math.hypot(max(sx-px,0,px-sx-sw),max(sy-py+16,0,py-16-sy-sh))
            proximity=max(0.,1-screen_distance/100)
            light=(.12+.06*math.sin(self.time*2+rank))*proximity
            wind=0.
            if stage==1:
                light+=pulse(self.time-state['arc'],.65)*.4
                vx,vy=state['vent_origin']
                wind=pulse(self.time-state['vent'],2.8)*max(0,1-math.hypot(px-vx,py-vy)/160)
            elif stage==3:
                light*=.4+.4*(math.sin(self.time*.9)**8)
            elif stage==4:light+=pulse(self.time-state['build'],2)*.13
            scan_age=self.time-state['scan']
            self.avatar=dict(light=COLORS[stage],strength=round(light*16)/16,
                             wind=round(wind*math.sin(self.time*22)),
                             settle=max(0.,1-(self.time-self.settle_at)/.8)*math.sin((self.time-self.settle_at)*24),
                             scan=scan_age/1.4 if stage==2 and 0<=scan_age<1.4 else -1.)
        self.previous=sample

    def room(self, rank):
        if not self.enabled:return {}
        state=self.rooms[rank]
        return dict(time=self.time,stage=rank//3,
                    **{key:self.time-state[key] for key in ('wake','vent','arc','scan','build','shake','moth')},
                    hero=state['hero'],reflection=state['reflection'],echo=state['echo'],
                    vent_origin=state['vent_origin'],
                    particles=[dict(p) for p in state['particles']])
