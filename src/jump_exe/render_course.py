"""Render the current five-stage course as a reviewable terrain overview."""
import argparse
from pathlib import Path
from .resources import ROOT
import cairo
from .art import tile,text
from .course import ROOMS
from .model import Tower,THEMES

NOTES = (
    ('YEAR 01 / MY CODE, MY KEYBOARD', 'Keycaps > AI disabled > autocomplete'),
    ('YEAR 02 / REVERT EVERYTHING', 'Build errors > PC cooling fan > git revert'),
    ('YEAR 03 / ONLY ON MY TERMS', 'Permissions > tests only > diff review'),
    ('YEAR 04 / I USED TO KNOW THIS', 'Session expired > lost shortcuts > 03:17'),
    ('YEAR 05 / ENJOY THE RIDE', 'Pair session > tests green > white pill'),
)


def render(path):
    tower = Tower((0,0,960,720),42)
    spans=[]
    for stage in range(5):
        rooms=[tower.rectangle(i) for i in range(stage*3,stage*3+3)]
        spans.append((max(y+h for x,y,w,h in rooms)-min(y for x,y,w,h in rooms))/2)
    footer=round(95+max(spans))
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24,2500,footer+155)
    c = cairo.Context(surface)
    c.set_source_rgb(.06,.075,.095)
    c.paint()
    for stage in range(5):
        origin = stage*500
        color = THEMES[stage][2]
        text(c,f'{stage+1:02} / {THEMES[stage][0]}',origin+16,32,22,color)
        group = list(range(stage*3,stage*3+3))
        top = min(tower.rectangle(i)[1] for i in group)
        for i in group:
            x,y,w,h = tower.rectangle(i)
            c.save()
            c.translate(origin+x/2,65+(y-top)/2)
            c.scale(.5,.5)
            tile(c,w,h,i,stage)
            c.restore()
        for row,line in enumerate(NOTES[stage]):
            text(c,line,origin+16,footer+row*23,12,color if row==0 else (.7,.73,.73))
        for row,i in enumerate(group):
            text(c,f'{i+1:02}  {ROOMS[i].title}',origin+16,footer+64+row*20,12)
    path.parent.mkdir(parents=True,exist_ok=True)
    surface.write_to_png(str(path))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/course-overview.png')
    render(parser.parse_args().output)
