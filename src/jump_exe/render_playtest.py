"""Render a continuous normal-physics climb without opening desktop windows."""
import argparse
import math
from pathlib import Path
from .resources import ROOT
import subprocess
import cairo
from .art import tile,knight,text
from .desktop_style import DEEP,TEXT,MUTED,ACCENTS
from .model import King,Tower,Camera,ledges,THEMES
from .physics_profile import PROFILE
from .routecheck import solve
from .story import Story


def render(path,seed=42):
    bounds=(0,0,1280,720)
    route=solve(bounds,seed)
    tower=Tower(bounds,seed);platforms=ledges(tower.near(0))
    king=King(*bounds[2:]);king.enter(platforms)
    camera=Camera(bounds);story=Story()
    path.parent.mkdir(parents=True,exist_ok=True)
    encoder=subprocess.Popen([
        'ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo',
        '-pixel_format','bgr0','-video_size','1280x720','-framerate','30',
        '-i','-','-an','-c:v','libx264','-preset','fast','-crf','22',
        '-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
    frame=0
    target=route[0]['target']

    def tick(direction=0):
        nonlocal frame
        king.step(PROFILE.tick,platforms,direction,bounds)
        camera.step(PROFILE.tick,king.y)
        story.update(PROFILE.tick,king,tower)
        frame+=1
        if frame%2:return
        surface=cairo.ImageSurface(cairo.FORMAT_RGB24,*bounds[2:])
        c=cairo.Context(surface);c.set_source_rgb(*DEEP);c.paint()
        for key,(x,y,w,h) in tower.near(0).items():
            y-=camera.offset
            if y+h<28 or y>720:continue
            rank=int(key)
            c.save();c.rectangle(0,28,1280,692);c.clip();c.translate(x,round(y))
            tile(c,w,h,rank,rank//3,story.time,accepted=story.accepted,
                 events=story.life.room(rank),ambient=story.atmosphere.room(rank))
            c.restore()
        knight(c,king.x,king.y-camera.offset,king.facing,king.charge,
               king.walk_phase if king.walking else story.time,king.scale,king.pose,
               story.atmosphere.avatar)
        stage=tower.level_at(king.y)
        text(c,f'{THEMES[stage][0]}  /  {king.jumps:02} JUMPS',18,20,13,ACCENTS[stage])
        text(c,'NORMAL PHYSICS REPLAY / SEED '+str(seed),850,20,12,TEXT)
        text(c,'NEXT '+target,18,698,12,MUTED)
        surface.flush();encoder.stdin.write(surface.get_data())

    try:
        for _ in range(60):tick()
        for witness in route:
            target=witness['target']
            king.cancel()
            for _ in range(math.ceil(king.recovery/PROFILE.tick)+1):tick()
            for _ in range(12):tick()
            for _ in range(witness['walk_ticks']):tick(witness['walk_direction'])
            king.press()
            for _ in range(witness['charge_frames']):tick()
            king.release(witness['direction'])
            for _ in range(180):
                tick()
                if king.room is not None:break
            if king.room!=target:
                raise RuntimeError(f'Replay landed on {king.room}, expected {target}')
        for _ in range(120):tick()
    finally:
        encoder.stdin.close()
        if encoder.wait():raise RuntimeError('Video encoding failed')
    print(f'{len(route)} jumps, {frame/60:.1f} seconds: {path}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/course-playthrough.mp4')
    parser.add_argument('--seed',type=int,default=42)
    args=parser.parse_args();render(args.output,args.seed)
