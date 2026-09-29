"""Replay the real climb, collect the pill, and render the ending without GUI windows."""
import math
from pathlib import Path
from .resources import ROOT
import subprocess
import cairo
from .art import tile,hud
from .desktop_style import DEEP
from .ending import focus_summit
from .model import King,Tower,Camera,ledges
from .story import Story,world_point
from .course import WHITE_PILL
from .routecheck import solve
from .physics_profile import PROFILE
from .music import ASSETS,VOLUME
from .sound import VOLUME as EFFECT_VOLUME


def prepare():
    bounds=(0,0,1280,720);tower=Tower(bounds,42);p=ledges(tower.near(0))
    king=King(*bounds[2:]);king.enter(p);camera=Camera(bounds);story=Story()

    def tick(direction=0):
        king.step(PROFILE.tick,p,direction,bounds)
        camera.step(PROFILE.tick,king.y)
        story.update(PROFILE.tick,king,tower)

    for jump in solve(bounds,42):
        king.cancel()
        for _ in range(math.ceil(king.recovery/PROFILE.tick)+13):tick()
        for _ in range(jump['walk_ticks']):tick(jump['walk_direction'])
        king.press()
        for _ in range(jump['charge_frames']):tick()
        king.release(jump['direction'])
        for _ in range(180):
            tick()
            if king.room is not None:break
        assert king.room==jump['target']
    px,_=world_point(tower,*WHITE_PILL)
    for _ in range(120):
        if story.ending.active:break
        tick(1 if px>king.x else -1)
    assert story.ending.active,'Climb did not collect the white pill'
    king.cancel()
    return tower,king,camera,story


def frame(tower,king,camera,story):
    out=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720)
    c=cairo.Context(out);c.set_source_rgb(*DEEP);c.paint()
    for key,(x,y,w,h) in tower.near(0).items():
        y-=camera.offset
        if y+h<28 or y>720:continue
        rank=int(key)
        c.save();c.rectangle(0,28,1280,692);c.clip();c.translate(x,round(y))
        tile(c,w,h,rank,rank//3,story.time,story.accepted,events=story.life.room(rank),
             ending=story.ending.state())
        c.restore()
    hud(c,1280,720,dict(ending=story.ending.state(),sprite_scale=king.scale,focused=True))
    return out


def render():
    tower,king,camera,story=prepare()
    docs=ROOT/'docs';docs.mkdir(exist_ok=True)
    path=docs/'ending-preview.mp4'
    encoder=subprocess.Popen([
        'ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo',
        '-pixel_format','bgr0','-video_size','1280x720','-framerate','24','-i','-',
        '-i',str(ASSETS/'trionfo-sereno.opus'),'-i',str(ASSETS/'sfx/white_pill.wav'),
        '-filter_complex',f'[1:a]volume={VOLUME}[bg];[2:a]volume={EFFECT_VOLUME}[cue];'
                          '[bg][cue]amix=inputs=2:duration=first:normalize=0[a]',
        '-map','0:v','-map','[a]','-t','20','-c:v','libx264','-preset','fast','-crf','20',
        '-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(path)],
        stdin=subprocess.PIPE)
    sheet=cairo.ImageSurface(cairo.FORMAT_RGB24,1280,720);board=cairo.Context(sheet)
    checkpoints=(36,80,206,300)
    try:
        for i in range(480):
            if i:
                story.update(1/24,king,tower)
                focus_summit(camera,tower,1/24)
            surface=frame(tower,king,camera,story)
            if i==444:surface.write_to_png(str(docs/'ending-preview.png'))
            if i in checkpoints:
                n=checkpoints.index(i)
                board.save();board.translate(n%2*640,n//2*360);board.scale(.5,.5)
                board.set_source_surface(surface,0,0);board.get_source().set_filter(cairo.FILTER_NEAREST)
                board.paint();board.restore()
            if i==206:surface.write_to_png(str(docs/'summit-pickup.png'))
            surface.flush();encoder.stdin.write(surface.get_data())
    finally:
        encoder.stdin.close()
        if encoder.wait():raise RuntimeError('Ending video encoding failed')
    sheet.write_to_png(str(docs/'ending-storyboard.png'))
    print(f'57-jump climb + pill collected; ending stats: {story.ending.stats}')
    print(path)


if __name__=='__main__':render()
