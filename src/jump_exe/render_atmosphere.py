"""Five real-input demonstrations of the reactive desktop, without GUI windows."""
from pathlib import Path
import subprocess
import cairo

from .resources import ROOT
from .art import tile,knight,text
from .course import ROOMS
from .model import King,Tower,ledges,THEMES
from .physics_profile import PROFILE
from .story import Story
from .desktop_style import DEEP,TEXT,MUTED,ACCENTS


SAMPLES=(
    (0,'home',20,1,'GHOST SUGGESTIONS',('An alternate jump flickers into view.',
       'Landing discards it as text.','Old terminals wake, then decline AI.')),
    (4,'valve',27,1,'HOT HARDWARE',('Vents disturb paper and clothing.',
       'Cable arcs light the developer red.','Impacts shake loose screws and dust.')),
    (6,'pan',12,0,'PERMISSION TO PROCEED',('A scan outlines the passing developer.',
       'APPROVED stamps the result.','Permission slips settle on hardware.')),
    (11,'entry',12,0,'AFTER HOURS',('Dust lifts from neglected equipment.',
       'Dark glass holds a delayed reflection.','Weak screen light follows the developer.')),
    (12,'branch',12,0,'WORK THAT CONNECTS',('Landings send packets through traces.',
       'Little builds finish in nearby terminals.','Checks rise as the hardware wakes.')),
)


class Sample:
    def __init__(self,spec):
        self.spec=spec;self.rank=spec[0]
        self.bounds=(0,0,480,360);self.tower=Tower(self.bounds,42)
        self.platforms=ledges(self.tower.near(0));self.king=King(480,360)
        self.story=Story();self.tick_count=0
        p=self.platforms[f'{self.rank}:{spec[1]}']
        self.king.land(p,p.left+(p.right-p.left)*(.25 if self.rank==0 else .5))
        if self.rank in (4,11):
            self.king.room=None;self.king.y-=35;self.king.vy=650
        self.story.update(0,self.king,self.tower)

    def tick(self):
        if self.tick_count==66:self.king.press()
        if self.tick_count==66+self.spec[2]:self.king.release(self.spec[3])
        self.king.step(PROFILE.tick,self.platforms,0,self.bounds)
        self.story.update(PROFILE.tick,self.king,self.tower)
        self.tick_count+=1

    def image(self):
        out=cairo.ImageSurface(cairo.FORMAT_RGB24,1100,720)
        c=cairo.Context(out);c.set_source_rgb(*DEEP);c.paint()
        rank=self.rank;room=ROOMS[rank];w,h=room.rect[2:]
        rx,ry,_,_=self.tower.rectangle(rank);k=self.king
        clip=max(0,min(h-300,k.y-ry-235))
        text(c,f'{rank//3+1:02} / {THEMES[rank//3][0]}',24,35,21,ACCENTS[rank//3])
        c.save();c.rectangle(24,62,600,600);c.clip();c.translate(24,62-round(clip)*2)
        tile(c,w*2,h*2,rank,rank//3,self.story.time,
             events=self.story.life.room(rank),ambient=self.story.atmosphere.room(rank))
        knight(c,(k.x-rx)*2,(k.y-ry)*2,k.facing,k.charge,self.story.time,2,k.pose,
               self.story.atmosphere.avatar)
        c.restore()
        text(c,self.spec[4],652,115,18,ACCENTS[rank//3])
        for i,line in enumerate(self.spec[5]):text(c,line,652,155+i*28,13,TEXT)
        text(c,'ACTUAL PHYSICS + PROXIMITY EVENTS',652,304,12,MUTED)
        text(c,'Native pixels / cosmetic reactions',24,698,12,MUTED)
        return out


def render():
    docs=ROOT/'docs';docs.mkdir(exist_ok=True)
    encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','rawvideo','-pixel_format','bgr0','-video_size','1100x720','-framerate','24','-i','-',
        '-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',
        '-movflags','+faststart',str(docs/'living-desktop.mp4')],stdin=subprocess.PIPE)
    sheet=cairo.ImageSurface(cairo.FORMAT_RGB24,1100,720*5)
    board=cairo.Context(sheet)
    try:
        for n,spec in enumerate(SAMPLES):
            sample=Sample(spec)
            snapshot=(40,7,18,39,18)[n]
            for i in range(144):
                while sample.tick_count/60<i/24:sample.tick()
                surface=sample.image()
                if i==snapshot:
                    surface.write_to_png(str(docs/f'living-desktop-{n+1}.png'))
                    board.set_source_surface(surface,0,n*720);board.paint()
                surface.flush();encoder.stdin.write(surface.get_data())
    finally:
        encoder.stdin.close()
        if encoder.wait():raise RuntimeError('Environmental preview encoding failed')
    sheet.write_to_png(str(docs/'living-desktop.png'))
    print(docs/'living-desktop.mp4')


if __name__=='__main__':render()
