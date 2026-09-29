"""Review every room at one pixel scale, using the actual game renderer."""
import argparse
from pathlib import Path
from .resources import ROOT
import cairo
from .art import tile, text, knight
from .course import ROOMS
from .desktop_style import BG, DEEP, TEXT, MUTED, ACCENTS
from .life import DesktopLife
from .model import THEMES


CAPTIONS = (
    'Familiar tools. Suggestions shut out. A routine worth defending.',
    'Retried builds. Hot hardware. A growing pile of discarded fixes.',
    'A little help, with conditions. Every permission still negotiated.',
    'Unanswered prompts. Forgotten shortcuts. Someone left the light on.',
    'Shared direction. Useful work. The keyboard is still yours.',
)


def encounters(rank, t):
    # Representative approach every eight seconds, then a return to resting.
    events = DesktopLife().room(rank)
    age = t % 8 - 1
    for event in events:
        event.update(age=age, active=0 <= age < event['duration'],
                     perched=age < 0 or age > 6, visits=int(age >= 0),
                     spin=max(0, min(age, 5))*2)
    return events


def render(path, stage, t=2.5):
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, 1800, 1080)
    c = cairo.Context(out)
    c.set_source_rgb(*DEEP);c.paint()
    accent = ACCENTS[stage]
    text(c, f'{stage+1:02} / {THEMES[stage][0]}', 28, 36, 23, accent)
    text(c, CAPTIONS[stage], 28, 62, 15, TEXT)
    ranks = list(range(stage*3, stage*3+3))
    width = sum(ROOMS[i].rect[2]*2 for i in ranks)+48
    left = (1800-width)/2
    for rank in ranks:
        room = ROOMS[rank]
        w, h = room.rect[2:]
        text(c, f'{rank+1:02} / {room.title}', left, 94, 12, accent)
        c.save();c.translate(left, 108)
        tile(c, w*2, h*2, rank, stage, t, events=encounters(rank,t))
        c.scale(2,2)
        block = next(b for b in room.blocks if b.name == room.route[0])
        x = block.x+block.w*(.24 if rank == 0 else .8 if rank == 6 else .5)
        knight(c, x, block.y, 1, 0, t, 1., 'idle')
        c.restore()
        left += w*2+24
    text(c, 'Actual room art at 2x / representative encounter previews / desktop wallpaper remains unchanged',
         28, 1070, 11, MUTED)
    if path is not None:
        path.parent.mkdir(parents=True,exist_ok=True)
        out.write_to_png(str(path))
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/world-review')
    parser.add_argument('--frames',type=int,default=1)
    args = parser.parse_args()
    if args.frames == 1:
        for stage in range(5):render(args.output/f'{stage+1:02}-{THEMES[stage][0].lower()}.png',stage)
    else:
        for i in range(args.frames):
            stage = min(4,i*5//args.frames)
            t = (i%(args.frames//5))/24
            render(args.output/f'{i:04}.png',stage,t)
