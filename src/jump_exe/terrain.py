"""Physical computer hardware and solid software controls, using shared colliders."""
import cairo
from .course import ROOMS
from .model import exposed_top
from .environment import rect,label
from .desktop_style import BG,DEEP,PANEL,MUTED,TEXT,WHITE,JADE,GREEN,CYAN,RED,YELLOW,BLUE,ACCENTS,SCENES,mix

LABELS={
    0:{'home':'HOME','spacebar':'SPACE','loft':'main.py [+]'},
    1:{'middle':'AGENTS OFF','upper':'AI OFF'},
    2:{'entry':'TAB','exit':'ACCEPT?','base':'TERMINAL'},
    3:{'entry':'E:BUILD','shard':'E:TEST','lip':'E:TYPE'},
    4:{'entry':'GPU','tooth':'RAM','valve':'CPU','rim':'VRAM','exit':'RETRY'},
    5:{'entry':'- fix','flange':'- fix2','release':'- undo','exit':'REVERT','floor':'main  -999'},
    6:{'entry':'ALLOW ONCE','pan':'DENY','beam':'ASK EVERY TIME','exit':'THIS FILE'},
    7:{'entry':'UNIT TESTS','fold':'INTEGRATION','exit':'ONLY TESTS'},
    8:{'entry':'+ patch','latch':'REVIEW','cap':'+ new','arch':'- old','hinge':'+ change','exit':'APPROVE'},
    9:{'entry':'DISCONNECTED','rim':'SLEEP'},
    10:{'entry':'ESC','control':'CTRL','undo':'Z','exit':'?'},
    12:{'entry':'USB-C','fork':'AGENT','branch':'YOU','exit':'CONNECTED'},
    13:{'entry':'BUILD OK','bridge':'TESTS','exit':'MERGE'},
    14:{'entry':'SPACE','landing':'SHIFT','bridge':'RUN','bank':'CHECKS PASS','release':'CTRL','summit':'ENTER'},
}


def caption(c,word,x,y,w,h,color=TEXT):
    if w<14 or h<12 or not word:return
    size=min(8,(w-12)/max(1,len(word))/.6,h-6)
    label(c,word,x+6,y+min(h-4,(h+size)/2),size,color)


def surfaces(c,rank):
    blocks=ROOMS[rank].blocks
    rectangles=[(b.x,b.y,b.w,b.h) for b in blocks]
    accent=ACCENTS[rank//3]
    scene=SCENES[rank//3]
    for b in blocks:
        x,y,w,h=b.x,b.y,b.w,b.h
        kind=b.material
        word=LABELS.get(rank,{}).get(b.name,'')
        c.save();c.rectangle(x,y,w,h);c.clip()
        # An opaque body and bevel distinguish solid terrain from thin background UI.
        rect(c,x,y,w,h,DEEP)
        rect(c,x+1,y+1,w-2,h-3,mix(scene['panel'],scene['metal'],.22))
        rect(c,x+1,y+1,w-2,1,mix(accent,WHITE,.3))
        rect(c,x+1,y+h-3,w-2,2,mix(DEEP,PANEL,.5))
        if kind=='key':
            cap=mix(TEXT,WHITE,.38) if rank<3 else mix(BLUE,scene['metal'],.35) if rank==10 else mix(CYAN,WHITE,.63)
            rect(c,x+2,y+2,w-4,h-5,mix(cap,BG,.35))
            rect(c,x+5,y+3,w-10,h-10,cap)
            rect(c,x+6,y+4,w-12,1,WHITE)
            rect(c,x+3,y+h-6,w-6,2,mix(cap,BG,.6))
            caption(c,word or 'RETURN',x+2,y-2,w-4,h,DEEP)
        elif kind in ('crt','case'):
            rect(c,x+2,y+3,w-4,h-6,mix(scene['metal'],scene['panel'],.4))
            if w>=36 and h>=40:
                rect(c,x+6,y+9,w-12,h-28,DEEP)
                for row in range(max(1,(h-40)//8)):
                    rect(c,x+10,y+15+row*8,max(1,w-28-row%3*3),1,mix(JADE,BG,.2))
                for px in range(x+7,x+w-6,5):rect(c,px,y+h-12,2,5,DEEP)
                rect(c,x+w-8,y+h-6,2,2,CYAN)
            elif w>h:
                for px in range(x+7,x+w-5,6):rect(c,px,y+6,2,h-12,DEEP)
                if word:
                    rect(c,x+5,y+4,min(w-10,len(word)*4+5),h-8,DEEP)
                    caption(c,word,x,y,w,h,scene['ink'])
            else:
                rect(c,x+3,y+5,2,h-10,MUTED)
                for py in range(y+10,y+h-5,10):rect(c,x+6,py,w-10,2,DEEP)
        elif kind=='board':
            rect(c,x+1,y+2,w-2,h-5,mix(scene['panel'],JADE,.15))
            for i,px in enumerate(range(x+6,x+w-8,28)):
                yy=y+6+i%2*5
                rect(c,px,yy,17,1,mix(YELLOW,BG,.6))
                rect(c,px+17,yy,1,5,mix(YELLOW,BG,.6))
                rect(c,px+7,y+h-9,9,5,DEEP)
                for p in range(3):rect(c,px+8+p*3,y+h-10,1,1,MUTED)
        elif kind=='heatsink':
            copper=(.54,.34,.24)
            rect(c,x+1,y+2,w-2,h-5,mix(copper,DEEP,.3))
            if w>h:
                for px in range(x+4,x+w-3,4):
                    rect(c,px,y+4,1,h-8,mix(copper,WHITE,.3))
                    rect(c,px+1,y+4,1,h-8,DEEP)
                if word:
                    length=min(w-8,len(word)*5+8)
                    rect(c,x+(w-length)/2,y+3,length,h-6,PANEL)
                    caption(c,word,x+(w-length)/2-1,y,length+2,h,TEXT)
            else:
                for py in range(y+4,y+h-3,4):
                    rect(c,x+3,py,w-6,1,copper);rect(c,x+3,py+1,w-6,1,DEEP)
        elif kind=='battery':
            outline_color=mix(BLUE,scene['metal'],.55)
            rect(c,x+3,y+3,w-6,h-6,outline_color)
            rect(c,x+6,y+6,w-12,h-12,DEEP)
            for py in range(y+16,y+h-17,21):
                rect(c,x+10,py,w-20,14,mix(BG,BLUE,.12))
            rect(c,x+10,y+h-27,w-20,10,mix(RED,BG,.2))
            label(c,'1%',x+9,y+18,9,BLUE)
        elif kind=='cable':
            rect(c,x+1,y+2,w-2,h-4,mix(scene['panel'],CYAN,.18))
            if w>h:
                for i,col in enumerate((JADE,CYAN,TEXT)):
                    yy=y+4+i*max(1,(h-8)/3)
                    rect(c,x+3,yy,w-6,1,mix(col,scene['panel'],.25))
                for px in (x+2,x+w-9):
                    rect(c,px,y+3,7,h-6,MUTED)
                    rect(c,px+2,y+5,3,max(1,h-10),DEEP)
                if word:
                    length=min(w-20,len(word)*4+8)
                    rect(c,x+(w-length)/2,y+3,length,h-6,PANEL)
                    caption(c,word,x+(w-length)/2-2,y,length+4,h,CYAN)
            else:
                rect(c,x+2,y+3,w-4,h-6,PANEL)
                for py in range(y+9,y+h-5,16):
                    rect(c,x+5,py,w-10,8,DEEP)
                    rect(c,x+7,py+2,max(1,w-14),3,MUTED)
                    rect(c,x+3,py+2,1,2,CYAN)
        elif kind=='desk':
            wood=(.30,.26,.18)
            rect(c,x+1,y+2,w-2,h-5,wood)
            for py in range(y+5,y+h-3,6):rect(c,x+3,py,w-6,1,mix(wood,DEEP,.25))
            rect(c,x+1,y+1,w-2,2,mix(TEXT,wood,.45))
            for px in (x+6,x+w-8):rect(c,px,y+6,2,2,DEEP)
        else:
            # Chunky application controls with readable labels: geometry remains solid.
            color=RED if kind=='error' or rank==5 else accent
            if kind=='diff':color=RED if rank==5 or b.x<90 else GREEN
            fill=mix(scene['panel'],color,.16)
            if rank//3==2:fill=mix(scene['metal'],scene['panel'],.38)
            rect(c,x+2,y+3,w-4,h-6,fill)
            rect(c,x+1,y+1,w-2,2,mix(color,WHITE,.3))
            if kind=='toggle':
                rect(c,x+4,y+4,5,max(2,h-8),color)
                caption(c,word,x+6,y,w-6,h,WHITE)
            elif kind in ('file','tab'):
                rect(c,x+3,y+3,5,h-6,mix(PANEL,WHITE,.18))
                caption(c,word or 'app.py',x+5,y,w-5,h,TEXT)
            elif kind=='diff' and h>35:
                for py in range(y+7,y+h-5,7):
                    rect(c,x+3,py,w-6,3,mix(BG,color,.28))
                    rect(c,x+4,py+1,3,1,color)
            else:
                caption(c,word,x,y,w,h,color if kind=='error' else TEXT)
            if kind=='panel':
                rect(c,x+w-7,y+5,3,3,GREEN if rank>=12 else MUTED)

        c.restore()
    for b,shape in zip(blocks,rectangles):
        light=WHITE if b.material=='key' else mix(ACCENTS[rank//3],WHITE,.38)
        for a,z in exposed_top(shape,rectangles):rect(c,a,b.y,z-a,1,light)
