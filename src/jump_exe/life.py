"""Player-triggered desktop encounters. This module only reads gameplay state."""
from dataclasses import dataclass
import math
from .course import ROOMS


@dataclass(frozen=True)
class Encounter:
    room: int
    kind: str
    anchor: str
    fraction: float = .5
    radius: float = 58
    duration: float = 3.
    cooldown: float = 10.
    message: str = ''
    trigger: str = 'near'


ENCOUNTERS=(
    Encounter(0,'duck','home',.2,50,3.,12.),
    Encounter(1,'notice','entry',.5,60,3.,14.,'suggestion hidden'),
    Encounter(2,'wake','chin',.4,80,4.,10.,'welcome back'),
    Encounter(3,'bugs','entry',.45,56,2.,12.),
    Encounter(4,'fan','valve',.5,170,5.,7.,'cooling down...','land'),
    Encounter(5,'diff','release',.5,300,2.5,3.,'reverted.','bonk'),
    Encounter(6,'cursor','entry',.4,58,3.,10.,'allow this jump?'),
    Encounter(7,'checks','fold',.5,64,3.,10.,'jump.test: PASS'),
    Encounter(8,'cursor','latch',.5,62,3.,10.,'one more line...'),
    Encounter(9,'wake','entry',.5,65,3.5,12.,'still there?'),
    Encounter(10,'duck','control',.65,62,3.,14.),
    Encounter(11,'lamp','entry',.25,100,4.,8.),
    Encounter(12,'penguin','branch',.25,66,3.,10.,'hello, human.'),
    Encounter(13,'checks','bridge',.5,85,3.,8.,'all green.'),
    Encounter(14,'penguin','landing',.25,70,3.,12.),
    Encounter(0,'ghost','loft',.35,75,4.,13.),
    Encounter(11,'cat','shelf',.75,65,4.,14.),
    Encounter(12,'bot','fork',.82,68,4.,9.),
)


class DesktopLife:
    def __init__(self):
        self.time=0.
        self.states=[]
        for spec in ENCOUNTERS:
            block=next(b for b in ROOMS[spec.room].blocks if b.name==spec.anchor)
            self.states.append(dict(x=block.x+block.w*spec.fraction,y=block.y,
                                    start=None,last=-1e6,armed=True,direction=1,
                                    visits=0,spin=0.,perched=True))

    def update(self,dt,king,tower,landing=False,bounced=False):
        dt=max(0.,min(dt,.1))
        self.time+=dt
        for spec,state in zip(ENCOUNTERS,self.states):
            rx,ry,w,h=tower.rectangle(spec.room)
            rw,rh=ROOMS[spec.room].rect[2:]
            px=(king.x-rx)*rw/w;py=(king.y-ry)*rh/h
            near=math.hypot(px-state['x'],py-state['y'])<spec.radius
            far=math.hypot(px-state['x'],py-state['y'])>spec.radius*1.7
            if far and self.time-state['last']>spec.cooldown:
                state['armed']=True
                state['perched']=True
            event=near and (spec.trigger=='near' or spec.trigger=='land' and landing
                           or spec.trigger=='bonk' and bounced)
            if event and state['armed']:
                state['start']=state['last']=self.time
                state['armed']=False
                state['perched']=False
                state['direction']=1 if px<state['x'] else -1
                state['visits']+=1
            age=None if state['start'] is None else self.time-state['start']
            if spec.kind=='fan' and age is not None and age<spec.duration:
                state['spin']+=dt*6*math.sin(math.pi*age/spec.duration)

    def room(self,rank):
        result=[]
        for spec,state in zip(ENCOUNTERS,self.states):
            if spec.room!=rank:continue
            age=-1. if state['start'] is None else self.time-state['start']
            active=0<=age<spec.duration
            result.append(dict(kind=spec.kind,x=state['x'],y=state['y'],age=age,
                               active=active,perched=state['perched'],
                               direction=state['direction'],spin=state['spin'],
                               message=spec.message,visits=state['visits'],
                               duration=spec.duration))
        return result
