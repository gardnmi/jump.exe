"""Render three real physics-driven encounters without capturing the desktop."""
import argparse
from pathlib import Path
import cairo
from .art import tile,text,knight
from .model import King,Tower,ledges
from .physics_profile import PROFILE
from .story import Story
from .desktop_style import DEEP,TEXT,CYAN,MUTED,JADE


class Sample:
    def __init__(self,rank):
        self.rank=rank
        self.bounds=(0,0,480,360)
        self.tower=Tower(self.bounds,42)
        self.platforms=ledges(self.tower.near(0))
        self.king=King(480,360)
        self.story=Story()
        if rank==0:self.king.enter(self.platforms)
        elif rank==4:
            p=self.platforms['4:entry']
            self.king.x=(p.left+p.right)/2;self.king.y=p.y-40
        else:
            p=self.platforms['12:branch']
            self.king.land(p,p.left+(p.right-p.left)*.92)

    def tick(self):
        t=self.story.time
        direction=(1 if self.rank==0 else -1) if .4<t<1. else 0
        if self.rank==4:direction=0
        self.king.step(PROFILE.tick,self.platforms,direction,self.bounds)
        self.story.update(PROFILE.tick,self.king,self.tower)


def render(path,samples):
    out=cairo.ImageSurface(cairo.FORMAT_RGB24,1920,950)
    c=cairo.Context(out);c.set_source_rgb(*DEEP);c.paint()
    text(c,'A LIVING DESKTOP / ACTUAL PROXIMITY + LANDING EVENTS',24,34,21,TEXT)
    labels=(('DEBUG DUCK','Walk closer: it startles, flaps and flies away.'),
            ('HOT HARDWARE','Land nearby: the PC fan spins up, then settles.'),
            ('LINUX COMPANY','Approach: a little penguin hops and greets you.'))
    for i,sample in enumerate(samples):
        rank=sample.rank
        x,y,w,h=sample.tower.rectangle(rank)
        origin=i*640+(640-w*2)/2
        text(c,labels[i][0],i*640+24,71,16,CYAN)
        c.save();c.translate(origin,98);c.scale(2,2)
        tile(c,w,h,rank,rank//3,sample.story.time,
             talking=sample.story.guide_near,events=sample.story.life.room(rank))
        for px,py,vx,vy,life,gold in sample.story.particles:
            c.set_source_rgba(*JADE,min(1,life*3));c.rectangle(round(px-x),round(py-y),1,1);c.fill()
        k=sample.king
        knight(c,k.x-x,k.y-y,k.facing,0,k.walk_phase if k.walking else sample.story.time,1,k.pose)
        c.restore()
        text(c,labels[i][1],i*640+24,906,14,TEXT)
    text(c,'Native scene rendering / normal movement and collision / encounters do not alter the jump',24,935,11,MUTED)
    out.write_to_png(str(path))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--frames',type=int,default=120)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    samples=[Sample(rank) for rank in (0,4,12)]
    tick=0
    for i in range(args.frames):
        while tick/60<i/24:
            for sample in samples:sample.tick()
            tick+=1
        render(args.output/f'{i:04}.png',samples)
