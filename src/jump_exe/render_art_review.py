"""Inspect the actual sprite frames, solid surfaces and props together on one board."""
from pathlib import Path
from .resources import ROOT
import cairo
from .art import text,room_surface
from .character import FRAMES,frame
from .course import ROOMS
from .desktop_style import BG,DEEP,TEXT,MUTED,CYAN,JADE
from .environment import rect,object_art,capsule
from .critters import creature


def render(path):
    surface=cairo.ImageSurface(cairo.FORMAT_RGB24,1120,1288)
    c=cairo.Context(surface)
    c.set_source_rgb(*DEEP);c.paint()
    text(c,'THE JUMP.EXE / OMARCHY ART REVIEW',24,31,20,TEXT)
    text(c,'Actual game frames at 3x / hardware and controls at 2x / nearest-neighbor sampling',24,56,12,MUTED)
    for i,name in enumerate(FRAMES):
        x=24+(i%4)*275;y=77+(i//4)*164
        rect(c,x,y,250,145,BG)
        sprite=frame(name)
        c.save();c.translate(x+65,y+1);c.scale(3,3)
        c.set_source_surface(sprite,0,0);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
        text(c,name,x+12,y+134,12,CYAN)
    text(c,'SOLID SURFACES / shared geometry, palette, light direction and pixel grid',24,589,14,JADE)
    examples=((0,'home'),(4,'valve'),(5,'entry'),(6,'entry'),
              (7,'exit'),(8,'arch'),(12,'branch'),(14,'summit'))
    for i,(rank,name) in enumerate(examples):
        x=24+(i%4)*275;y=608+(i//4)*107
        b=next(b for b in ROOMS[rank].blocks if b.name==name)
        rect(c,x,y,250,91,BG)
        c.save();c.translate(x+(250-b.w*2)/2,y+8)
        c.rectangle(0,0,b.w*2,b.h*2);c.clip();c.scale(2,2)
        c.set_source_surface(room_surface(rank,True),-b.x,-b.y)
        c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
        text(c,f'{b.material} / {name}',x+10,y+81,11,TEXT)
    text(c,'SMALL PROPS / same native grid',24,857,14,JADE)
    items=(('keyboard','manual'),('lamp',''),('coffee',''),('chair',''),('cable','joined'),('pill',''),
           ('books',''),('notepad',''),('bin',''),('printer','error'),('plant',''),('crt','offline'))
    for i,(kind,value) in enumerate(items):
        temp=cairo.ImageSurface(cairo.FORMAT_ARGB32,64,44)
        q=cairo.Context(temp);q.set_antialias(cairo.ANTIALIAS_NONE)
        if kind=='pill':capsule(q,32,24,True,2.)
        else:object_art(q,kind,32,38,value,2.,4)
        x=24+(i%6)*182;y=873+(i//6)*126
        rect(c,x,y,166,113,BG)
        c.save();c.translate(x+19,y+2);c.scale(2,2)
        c.set_source_surface(temp,0,0);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
        text(c,kind,x+10,y+104,11,TEXT)
    text(c,'DESKTOP LIFE / original native-pixel creatures',24,1147,14,JADE)
    for i,(kind,flying) in enumerate((('duck',False),('duck',True),('bug',False),('penguin',True),
                                     ('cat',True),('bot',True))):
        x=24+i*182
        rect(c,x,1164,166,102,BG)
        temp=cairo.ImageSurface(cairo.FORMAT_ARGB32,40,24)
        q=cairo.Context(temp);q.set_antialias(cairo.ANTIALIAS_NONE)
        creature(q,kind,20,20,.5,1,flying)
        c.save();c.translate(x+23,1166);c.scale(3,3)
        c.set_source_surface(temp,0,0);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint();c.restore()
        text(c,kind+(' / react' if flying else ' / rest'),x+10,1255,11,TEXT)
    path.parent.mkdir(parents=True,exist_ok=True)
    surface.write_to_png(str(path))


if __name__=='__main__':
    render(ROOT/'docs/art-review.png')
