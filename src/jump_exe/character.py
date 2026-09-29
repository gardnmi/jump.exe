"""Original Omarchy developer and caretaker, sampled from a transparent atlas."""
from functools import lru_cache
from .resources import ASSETS
import cairo
from .physics_profile import PROFILE

# Tight source rectangles measured from the sheet's alpha, not assumed grid cells.
# The generated sheet has uneven padding; each pose shares the idle pixel scale.
FRAMES = {
    'idle': (95,36,260,347),
    'walk0': (430,36,632,347),
    'walk1': (783,36,995,347),
    'charge': (1142,120,1375,347),
    'rise': (70,373,307,659),
    'fall': (413,375,657,702),
    'bonk': (745,404,1050,690),
    'land': (1140,477,1384,702),
    'guide0': (57,729,324,1050),
    'guide1': (420,733,686,1050),
    'guide2': (777,729,1046,1050),
    'guide3': (1142,730,1399,1050),
}


@lru_cache(maxsize=1)
def atlas():
    return cairo.ImageSurface.create_from_png(
        str(ASSETS/'omarchy-developers.png'))


@lru_cache(maxsize=16)
def frame(pose, walk_frame=0):
    name = f'walk{walk_frame%2}' if pose == 'walk' else pose
    x1,y1,x2,y2 = FRAMES.get(name,FRAMES['idle'])
    ratio = PROFILE.sprite_height/(FRAMES['idle'][3]-FRAMES['idle'][1])
    w,h = (x2-x1)*ratio,(y2-y1)*ratio
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,40,40)
    c = cairo.Context(surface)
    # Tucked legs lift off the feet anchor during ascent and recoil.
    lift = 4 if pose == 'rise' else 2 if pose == 'bonk' else 0
    c.translate((40-w)/2,36-h-lift)
    c.rectangle(0,0,w,h)
    c.clip()
    c.scale(ratio,ratio)
    c.set_source_surface(atlas(),-x1,-y1)
    c.get_source().set_filter(cairo.FILTER_NEAREST)
    c.paint()
    return surface


def draw(c,x,y,facing,scale,pose,phase=0):
    sprite = frame(pose,int(phase)%2)
    c.save()
    c.translate(round(x),round(y))
    c.scale(facing*scale,scale)
    c.set_source_surface(sprite,-20,-36)
    c.get_source().set_filter(cairo.FILTER_NEAREST)
    c.paint()
    c.restore()


def guide(c,x,y,t,talking=False):
    poses = (0,1,1,3,0,2,0,3) if talking else (0,0,0,2,0,0,3,0)
    draw(c,x,y,1,1.,f'guide{poses[int(t*2)%len(poses)]}')
