"""A small pixel desktop epilogue, composed at the game's native pixel density."""
import math
import cairo
from .character import draw,guide
from .critters import creature
from .environment import rect,label,object_art
from .desktop_style import DEEP,BG,PANEL,TEXT,WHITE,MUTED,JADE,CYAN,YELLOW,SCENES,mix
from .ending import RESULT_AT,PROJECT_PROMPT,AGENT_REPLY

WIDTH,HEIGHT=420,280


def center(c,value,y,size=10,color=TEXT):
    from .desktop_style import FONT
    c.select_font_face(FONT,0,0);c.set_font_size(size)
    label(c,value,(WIDTH-c.text_extents(value).x_advance)/2,y,size,color)


def panel(c,x,y,w,h,title,color=CYAN):
    rect(c,x,y,w,h,color);rect(c,x+1,y+1,w-2,h-2,DEEP)
    rect(c,x+1,y+1,w-2,10,PANEL)
    rect(c,x+4,y+4,3,3,color)
    label(c,title,x+10,y+8,5,color)


def sparks(c,t,cx,cy,count=28):
    # Slow expanding clusters, never a full-screen flash.
    for i in range(count):
        age=(t+i*.091)%2.8
        a=i*2.39996
        r=8+age*(12+i%5*2)
        color=mix(BG,WHITE if i%3==0 else CYAN,max(0,1-age/2.8))
        rect(c,cx+math.cos(a)*r,cy+math.sin(a)*r-age*5,1+i%2,1+i%2,color)


def desk(c,t,hero_x=178):
    rect(c,79,232,264,5,mix(TEXT,JADE,.4))
    rect(c,82,237,258,6,PANEL)
    for x in (91,328):rect(c,x,243,5,10,MUTED)
    object_art(c,'keyboard',216,232,'manual',t,4)
    object_art(c,'coffee',251,232,'',t,4)
    object_art(c,'plant',316,232,'',t,4)
    draw(c,hero_x,232,1,1,'walk' if hero_x<178 else 'idle',t*8)
    creature(c,'bot',276,232-round(max(0,math.sin(t*2))*2),t,flying=True)
    creature(c,'duck',119,232,t)
    guide(c,369,252,t,True)
    object_art(c,'coffee',394,252,'',t,4)


def native(ending,focused=True):
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,WIDTH,HEIGHT)
    c=cairo.Context(surface);c.set_antialias(cairo.ANTIALIAS_NONE)
    t=ending.get('age',0.);stats=ending.get('stats',{})
    rect(c,0,0,WIDTH,HEIGHT,CYAN);rect(c,1,1,WIDTH-2,HEIGHT-2,DEEP)
    rect(c,2,12,WIDTH-4,HEIGHT-14,SCENES[4]['back'])
    rect(c,2,2,WIDTH-4,10,BG)
    label(c,'[+]  white-pill / a new chapter',7,9,5,TEXT)
    label(c,'~/code/what-next',328,9,5,JADE)
    # Fine circuit traces frame the stage without obscuring the scene.
    for x in (7,412):
        rect(c,x,23,1,228,mix(PANEL,JADE,.3))
        for y in range(32,251,29):rect(c,x-1,y,3,3,JADE)

    center(c,'THE WHITE PILL',39,18,WHITE)
    center(c,'CLIMB COMPLETE  /  ENJOY THE RIDE',55,8,CYAN)
    for i,(title,value) in enumerate((('YOUR TIME',stats.get('time','0:00')),
                                      ('JUMPS',str(stats.get('jumps',0))),
                                      ('LONGEST FALL',stats.get('fall','0.0')+' screens'))):
        x=19+i*130
        panel(c,x,68,122,47,title,JADE)
        label(c,value,x+10,101,11,WHITE)
    panel(c,95,126,230,62,'~/code/what-next')
    label(c,PROJECT_PROMPT,107,150,8,TEXT)
    label(c,AGENT_REPLY,107,170,7,CYAN)
    if int(t*2)%2:rect(c,108,176,5,6,WHITE)
    desk(c,t)
    sparks(c,(t-RESULT_AT)*.6,47,185,12)
    if stats.get('practice'):label(c,'PRACTICE RUN',20,250,5,JADE)
    center(c,'ENTER  Enjoy the view   R  Climb again   ESC  Exit',267,6,WHITE)
    if not focused:
        rect(c,87,18,246,14,DEEP)
        center(c,'PAUSED / click a platform window',28,7,YELLOW)
    return surface


def draw_finale(c,w,h,data):
    surface=native(data['ending'],data.get('focused',True))
    scale=min(data.get('sprite_scale',1),(w-24)/WIDTH,(h-56)/HEIGHT)
    c.save();c.translate(round((w-WIDTH*scale)/2),round((h-HEIGHT*scale)/2))
    c.scale(scale,scale)
    c.set_source_surface(surface,0,0);c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint()
    c.restore()
