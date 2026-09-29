"""Replay corrected shelf jumps with normal input and physics."""
import argparse
from pathlib import Path
from .resources import ROOT
import cairo
from .art import tile, knight, text
from .desktop_style import DEEP, TEXT, MUTED, CYAN, YELLOW, BLUE
from .model import King, Tower, ledges
from .physics_profile import PROFILE
from .story import Story
from .course import ROOMS


JUMPS = {
    'sleep': (9,'bell','rim',25,'BATTERY','SLEEP','Shelf moved left and down.'),
    'desk': (11,'shelf','exit',23,'RIGHT SHELF','UPPER SHELF','Overhang shortened and lowered.'),
    'revert': (5,'release','exit',26,'UNDO','REVERT','Overhang recessed; height unchanged.'),
    'tests': (7,'entry','fold',26,'UNIT TESTS','INTEGRATION','Test tabs recessed; heights unchanged.'),
    'tests-exit': (7,'fold','exit',26,'INTEGRATION','ONLY TESTS','Upper tab recessed; height unchanged.'),
    'ci': (13,'entry','bridge',28,'BUILD OK','TESTS','Small platform moved to the right.'),
    'ci-exit': (13,'bridge','exit',27,'TESTS','MERGE','Rail removed; MERGE overhang recessed.'),
}


class Replay:
    def __init__(self, jump='sleep'):
        (self.rank,source,target,self.charge_frames,self.source_label,
         self.target_label,self.change)=JUMPS[jump]
        self.target=f'{self.rank}:{target}'
        self.direction=1 if jump in ('revert','tests','ci') else -1
        self.fraction={'revert':1/3,'tests':.24,'tests-exit':.54,'ci':.2}.get(jump,.5)
        self.position={'revert':'LEFT THIRD','tests':'LEFT QUARTER','ci':'SUPPORTED LEFT SIDE'}.get(jump,'MIDDLE')
        self.tolerance=5 if jump in ('sleep','desk') else 3
        self.bounds=(0,0,2048,1152) if jump in ('revert','tests','tests-exit') else (0,0,1600,900)
        self.tower=Tower(self.bounds,42)
        self.platforms=ledges(self.tower.near(0))
        self.king=King(*self.bounds[2:])
        source=self.platforms[f'{self.rank}:{source}']
        self.king.land(source,source.left+(source.right-source.left)*self.fraction)
        self.story=Story()
        self.frame=0
        self.trace=[]
        self.bounced=False
        self.knocked=False

    def tick(self):
        if self.frame==42:self.king.press()
        if self.frame==42+self.charge_frames:self.king.release(self.direction)
        vx=self.king.vx
        self.king.step(PROFILE.tick,self.platforms,0,self.bounds)
        self.bounced |= vx*self.king.vx<0
        self.knocked |= self.king.knocked
        self.story.update(PROFILE.tick,self.king,self.tower)
        if self.king.room is None and self.frame%2==0:self.trace.append((self.king.x,self.king.y))
        self.frame+=1


def render(path,replay):
    height=max(1020,ROOMS[replay.rank].rect[3]*3+155)
    height+=height%2  # Keep review frames compatible with YUV420 video encoding.
    out=cairo.ImageSurface(cairo.FORMAT_RGB24,1000,height)
    c=cairo.Context(out);c.set_source_rgb(*DEEP);c.paint()
    text(c,f'{ROOMS[replay.rank].title} / DIRECT JUMP REVIEW',24,37,23,BLUE)
    text(c,'Normal walking + charged-jump physics / no dev flight',24,65,14,TEXT)
    rank=replay.rank;rx,ry,w,h=replay.tower.rectangle(rank);k=replay.king
    c.save();c.translate(24,105)
    rw,rh=ROOMS[rank].rect[2:]
    tile(c,rw*3,rh*3,rank,rank//3,replay.story.time,events=replay.story.life.room(rank),
         ambient=replay.story.atmosphere.room(rank))
    c.scale(3/k.scale,3/k.scale)
    for x,y in replay.trace:
        c.set_source_rgb(*YELLOW);c.rectangle(x-rx,y-ry,k.scale,k.scale);c.fill()
    knight(c,k.x-rx,k.y-ry,k.facing,k.charge,replay.story.time,k.scale,k.pose,
           replay.story.atmosphere.avatar)
    c.restore()
    direction='Right / D' if replay.direction>0 else 'Left / A'
    lines=((f'{replay.source_label} / {replay.position}',CYAN),('',TEXT),
           (f'Hold Space for ~{replay.charge_frames/60:.2f} seconds.',TEXT),(f'Release while holding {direction}.',TEXT),
           ('Keep the keyboard still in the air.',MUTED),('',TEXT),
           (replay.change,TEXT),('The jump now clears the shelf edge.',TEXT),
           ('No rebound is required.',CYAN),('',TEXT),
           (f'{replay.tolerance}+ consecutive charge frames work',TEXT),('across tested display shapes/seeds.',TEXT))
    for i,(line,color) in enumerate(lines):text(c,line,486,157+i*28,17 if i==0 else 15,color)
    if k.room==replay.target:status=f'LANDED / {replay.target_label}'
    elif k.room is None:status='JUMPING RIGHT' if replay.direction>0 else 'JUMPING LEFT'
    elif k.charging:status='CHARGING'
    else:status='READY'
    text(c,status,486,595,20,CYAN)
    text(c,f'{replay.charge_frames} charge frames / rebound: {replay.bounced}',486,625,14,MUTED)
    text(c,'Actual renderer + collision geometry. Yellow dots mark the feet through the jump.',24,height-31,12,MUTED)
    path.parent.mkdir(parents=True,exist_ok=True);out.write_to_png(str(path))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jump',choices=JUMPS,default='sleep')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--frames',type=int,default=1)
    args=parser.parse_args();replay=Replay(args.jump)
    if args.output is None:
        args.output=ROOT/f'docs/{args.jump}-jump-proof.png'
    if args.frames==1:
        for _ in range(150):replay.tick()
        assert replay.king.room==replay.target and not replay.knocked,'Replay did not clear the jump'
        render(args.output,replay)
    else:
        for i in range(args.frames):
            while replay.frame/60<i/24:replay.tick()
            render(args.output/f'{i:04}.png',replay)
