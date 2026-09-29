"""Render the game's actual art and animation without capturing the user's desktop."""
import argparse
from pathlib import Path
from .resources import ROOT
import cairo
from .art import tile, text, knight
from .course import ROOMS, SPAWN_FRACTION
from .model import THEMES
from .story import YEARS

CAPTIONS = (
    ('My code. My keyboard.', 'Giant keycaps. AI disabled. A familiar shell.'),
    ('Fixing the fix. Again.', 'Hot hardware. Failed builds. Revert all.'),
    ('You can help. On my terms.', 'Permission prompts. Tests only. Diff review.'),
    ('I used to know this.', 'Lost shortcuts. Unplugged tools. 03:17.'),
    ('You steer. It helps.', 'Shared terminals. Tests green. Enjoy the ride.'),
)


def render(path,t=2.):
    surface=cairo.ImageSurface(cairo.FORMAT_RGB24,2100,670)
    c=cairo.Context(surface)
    c.set_source_rgb(.045,.055,.065);c.paint()
    text(c,"JUMP.EXE / AN OMARCHY DESKTOP ASCENT",24,32,19)
    for stage,rank in enumerate((0,4,6,10,14)):
        color=THEMES[stage][2]
        left=stage*420
        text(c,f'{YEARS[stage]} / {THEMES[stage][0]}',left+24,68,16,color)
        room=ROOMS[rank]
        w,h=room.rect[2:]
        scale=min(370/w,455/h)
        c.save();c.translate(left+(420-w*scale)/2,94);c.scale(scale,scale)
        tile(c,w,h,rank,stage,t,talking=stage==0)
        name='landing' if stage==4 else room.route[0]
        p=next(b for b in room.blocks if b.name==name)
        knight(c,p.x+p.w*(SPAWN_FRACTION if rank==0 else .8 if rank==6 else .5),p.y,1,0,t,1.,'idle')
        c.restore()
        for i,line in enumerate(CAPTIONS[stage]):
            text(c,line,left+24,590+i*22,12,color if i==0 else (.64,.65,.59))
    text(c,'Omarchy / Osaka Jade palette / One native pixel grid / Actual in-game rendering',24,651,11,(.53,.57,.53))
    if path is not None:
        path.parent.mkdir(parents=True,exist_ok=True)
        surface.write_to_png(str(path))
    return surface


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/story-preview.png')
    parser.add_argument('--time',type=float,default=2.)
    parser.add_argument('--frames',type=int,default=1,help='Optional 24 fps sequence, named 0000.png etc in output directory')
    args=parser.parse_args()
    for i in range(args.frames):
        path=args.output if args.frames==1 else args.output/f'{i:04}.png'
        render(path,args.time+i/24)
