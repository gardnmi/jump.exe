"""Large pane-local silhouettes and rhythms that distinguish the five stages.

Drawn behind terrain at native resolution. These are recessed screen contents,
case texture and lighting; the bright, beveled collision edges remain foremost.
"""
import math
from .course import ROOMS
from .desktop_style import DEEP,TEXT,WHITE,JADE,GREEN,CYAN,RED,YELLOW,BLUE,SCENES,mix
from .environment import rect,label,glow


def outline(c,x,y,w,h,color):
    rect(c,x,y,w,1,color);rect(c,x,y+h-1,w,1,color)
    rect(c,x,y,1,h,color);rect(c,x+w-1,y,1,h,color)


def hatch(c,x,y,w,h,color,step=9):
    c.save();c.rectangle(x,y,w,h);c.clip()
    for i in range(-h,w+h,step):
        for j in range(h):rect(c,x+i+j,y+j,3,1,color)
    c.restore()


def foundation(c,rank):
    w,h=ROOMS[rank].rect[2:];stage=rank//3;s=SCENES[stage]
    rect(c,0,0,w,h,s['back'])
    if stage==0:
        # A cared-for personal machine: warm phosphor and a worn desk surface.
        rect(c,5,h-64,w-10,60,mix(s['back'],YELLOW,.045))
        for y in range(h-62,h-5,5):
            for x in range(8,w-8,37):
                rect(c,x,y,min(23,w-x-7),1,mix(s['back'],TEXT,.07))
        for x in (5,w-7):rect(c,x,14,2,h-23,mix(s['back'],JADE,.2))
        glow(c,w*.24,h*.78,w*.75,YELLOW,.12)
    elif stage==1:
        # Riveted oxidized metal and heat channels, not another editor backdrop.
        for x in range(8,w,36):
            rect(c,x,16,23,h-23,mix(s['back'],RED,.035))
            rect(c,x,16,1,h-23,mix(DEEP,RED,.12))
        for x in (6,w-12):
            for y in range(24,h-8,43):
                rect(c,x,y,5,5,mix(s['back'],s['metal'],.65))
                rect(c,x+1,y+2,3,1,DEEP)
        hatch(c,3,h-11,w-6,7,mix(s['back'],YELLOW,.4),12)
        glow(c,w*.7,h*.65,w*.8,RED,.12)
    elif stage==2:
        # An audited workstation: graph paper, ruled gutters and scope brackets.
        for x in range(10,w,12):rect(c,x,16,1,h-27,mix(s['back'],YELLOW,.06))
        for y in range(16,h,12):rect(c,8,y,w-16,1,mix(s['back'],YELLOW,.06))
        rect(c,6,17,2,h-30,mix(s['back'],YELLOW,.35))
        for y in range(20,h-18,20):rect(c,8,y,5,1,mix(s['back'],YELLOW,.5))
    elif stage==3:
        # Unlit glass. The dark center and dusty corners are intentionally empty.
        for i in range(80):
            x=3+(i*43)%(w-6);y=14+(i*61)%(h-19)
            if x<14 or x>w-17 or y>h-28:
                rect(c,x,y,1,1,mix(s['back'],BLUE,.16))
        rect(c,w-5,16,1,h-21,mix(s['back'],BLUE,.12))
    else:
        # A powered motherboard, broad lit traces and clear paired work areas.
        for i in range(5):
            x=12+i*17;y=h-24-i*7
            shade=mix(s['back'],CYAN,.16)
            rect(c,x,y,max(1,w-x-12),1,shade)
            rect(c,x,60,1,max(1,y-60),shade)
            rect(c,x-1,y-1,3,3,mix(s['back'],CYAN,.35))
        glow(c,w*.65,h*.25,w*.8,CYAN,.1)


def warning(c,x,y,size,color):
    # Pixel triangle; outline is recessed and has no platform-like top edge.
    for row in range(size):
        half=round(row*.58)
        rect(c,x-half,y+row,2,1,color);rect(c,x+half,y+row,2,1,color)
    rect(c,x-round(size*.58),y+size,round(size*1.16)+2,2,color)
    rect(c,x,y+size*.36,2,size*.35,color);rect(c,x,y+size*.82,2,2,color)


def padlock(c,x,y,size,color):
    # An etched permission icon, deliberately flat rather than a solid ledge.
    outline(c,x+size*.24,y,size*.52,size*.52,color)
    outline(c,x,y+size*.37,size,size*.67,color)
    rect(c,x+size*.45,y+size*.59,size*.13,size*.24,color)


def dressing(c,rank):
    w,h=ROOMS[rank].rect[2:];s=SCENES[rank//3]
    if rank==0:
        # Personal machine: taped photo and coffee rings, at human-object scale.
        rect(c,18,231,47,33,mix(s['back'],TEXT,.3))
        rect(c,20,233,43,27,mix(s['back'],JADE,.28))
        rect(c,34,230,15,4,mix(TEXT,s['back'],.45))
        for i in range(5):rect(c,23+i*7,245-i%3*3,7,11+i%3*3,mix(JADE,s['back'],.48))
        label(c,'first build',21,263,5,s['ink'])
    elif rank==1:
        # Oversized sealed integration card: the refusal is a visible object.
        rect(c,13,161,96,66,mix(DEEP,JADE,.07))
        outline(c,13,161,96,66,mix(s['back'],JADE,.6))
        padlock(c,49,171,23,mix(TEXT,JADE,.55))
        label(c,'NOT NEEDED',22,216,10,TEXT)
    elif rank==2:
        rect(c,62,153,98,48,mix(DEEP,JADE,.09))
        label(c,'JUST A',66,169,11,mix(TEXT,JADE,.55))
        label(c,'GUESS.',66,188,16,TEXT)
    elif rank==3:
        # A crashed display behind the three playable error notices.
        warning(c,126,75,21,mix(RED,YELLOW,.25))
        for points in (((8,19),(34,47),(23,63)),((137,18),(124,28),(129,38))):
            c.set_source_rgb(*mix(s['back'],RED,.5));c.set_line_width(1)
            c.move_to(*points[0])
            for point in points[1:]:c.line_to(*point)
            c.stroke()
    elif rank==4:
        # The fan is the landmark; its orange shroud reads even at thumbnail size.
        for r in (87,93,101):
            c.set_source_rgb(*mix(s['back'],s['metal'],.7));c.set_line_width(2)
            c.arc(139,232,r,0,math.tau);c.stroke()
        hatch(c,100,335,96,9,mix(s['back'],YELLOW,.45))
    elif rank==5:
        # Repeated reversions feed a paper shredder in the terminal's footer.
        rect(c,12,366,76,50,mix(DEEP,RED,.09))
        outline(c,12,366,76,50,mix(s['metal'],DEEP,.35))
        for x in range(18,82,7):rect(c,x,375,3,27,mix(s['back'],RED,.32))
        rect(c,19,361,60,8,DEEP)
        label(c,'DISCARD ALL',17,412,8,mix(TEXT,RED,.35))
    elif rank==6:
        padlock(c,35,182,46,mix(YELLOW,s['back'],.25))
        label(c,'ON MY',153,176,10,s['ink'])
        label(c,'TERMS.',153,190,12,YELLOW)
    elif rank==7:
        # A large test-file sheet behind the solid tabs, with a stamped boundary.
        rect(c,13,78,112,156,mix(s['panel'],TEXT,.15))
        rect(c,14,79,4,153,mix(s['metal'],YELLOW,.35))
        label(c,'TEST SCOPE',24,96,10,s['ink'])
        for row in range(5):
            y=106+row*8
            rect(c,24,y,3,3,YELLOW)
            rect(c,33,y+1,66-row%3*12,1,mix(s['ink'],s['panel'],.4))
        outline(c,26,184,85,30,mix(RED,s['back'],.35))
        label(c,'SOURCE',33,196,9,mix(TEXT,RED,.3))
        label(c,'LOCKED',33,207,10,mix(TEXT,RED,.3))
    elif rank==8:
        # Revision proof sheets: broad, contrasting ruled panels behind the route.
        for x,color in ((10,RED),(198,GREEN)):
            width=117 if x==10 else 66
            rect(c,x,88,width,138,mix(s['panel'],color,.09))
            rect(c,x+4,90,2,133,mix(s['back'],color,.55))
            for i in range(12):rect(c,x+11,97+i*10,width-17-i%3*4,2,mix(s['ink'],s['panel'],.72))
    elif rank==9:
        # Large severed USB ends: a recognizable absence of connection.
        rect(c,18,200,44,26,mix(s['panel'],BLUE,.06))
        outline(c,18,200,44,26,mix(s['panel'],BLUE,.22))
        rect(c,21,203,38,17,DEEP)
        for x in range(25,56,6):rect(c,x,207,2,8,mix(s['panel'],BLUE,.35))
        rect(c,68,200,8,23,mix(s['panel'],BLUE,.25))
        rect(c,73,204,12,15,mix(s['panel'],BLUE,.35))
    elif rank==10:
        # A ghost keyboard with entire switches missing, away from the solid keys.
        outline(c,13,182,69,47,mix(s['panel'],BLUE,.22))
        for row in range(3):
            for col in range(5):
                x=18+col*12;y=188+row*12
                outline(c,x,y,8,8,mix(s['panel'],BLUE,.28))
                rect(c,x+3,y+2,1,4,mix(BLUE,s['panel'],.6))
        label(c,'...',182,194,24,mix(s['panel'],BLUE,.2))
    elif rank==11:
        # Most of the editor is unlit; the single desk lamp supplies warmth.
        rect(c,14,93,112,99,mix(DEEP,s['back'],.25))
        label(c,'1',18,109,8,mix(s['panel'],BLUE,.4))
        glow(c,41,197,73,YELLOW,.2)
        c.set_source_rgba(*YELLOW,.07)
        c.move_to(44,187);c.line_to(6,216);c.line_to(110,216);c.close_path();c.fill()
    elif rank==12:
        # A drawn interface on the human side, a working version on the agent side.
        for x,color in ((20,CYAN),(166,GREEN)):
            rect(c,x,152,92,44,s['panel'])
            outline(c,x,152,92,44,mix(s['back'],color,.55))
            rect(c,x+1,153,90,8,mix(s['panel'],color,.25))
            for i in range(3):rect(c,x+6+i*5,156,2,2,color)
            for i in range(2):outline(c,x+6+i*43,168,36,21,mix(s['back'],color,.6))
        label(c,'DIRECTION',20,210,7,CYAN)
    elif rank==13:
        # One continuous green pipeline, materially different from the permission sheet.
        rect(c,8,62,119,65,mix(s['panel'],GREEN,.18))
        outline(c,8,62,119,65,mix(s['back'],GREEN,.5))
        label(c,'BUILD / TEST / SHIP',13,72,6,s['ink'])
    elif rank==14:
        # Finished work inhabits both terminal panes: shared, growing, illuminated.
        for x,color in ((19,CYAN),(154,GREEN)):
            for i in range(4):
                yy=380+i*15
                rect(c,x,yy,4,4,mix(color,WHITE,.25))
                rect(c,x+9,yy+1,71-i%2*15,2,mix(s['panel'],TEXT,.6))
        label(c,'STILL MAKING THINGS.',32,495,14,mix(TEXT,CYAN,.25))


def animate(c,rank,t):
    w,h=ROOMS[rank].rect[2:];stage=rank//3;s=SCENES[stage]
    if stage==1:
        # Heat and failed retries: local slow pulses, never a full-pane flash.
        phase=t%6
        for i in range(6):
            age=(t*.19+i/6)%1
            x=w*.45+math.sin(i*9+t*.4)*w*.25;y=h*.85-age*h*.48
            color=mix(s['back'],RED,(1-age)*.28)
            rect(c,x,y,2,3,color);rect(c,x-1,y+3,4,1,color)
        if rank==3:
            width=int(phase/6*103)
            rect(c,14,125,width,3,mix(RED,YELLOW,.25))
        elif rank==5:
            for i in range(5):
                y=322+(t*10+i*13)%65;x=22+i*11
                rect(c,x,y,4,8,mix(TEXT,RED,.3));rect(c,x+1,y+2,2,1,s['back'])
    elif stage==2:
        # A scope scanner advances, stops at the lock, then retreats.
        y=82+min((t%9)*20,90)
        for x in range(11,w-10,6):rect(c,x,y,2,1,mix(s['back'],YELLOW,.28))
    elif stage==3:
        # A cold screen reflection, interrupted lines and very slow settled dust.
        for i in range(7):
            x=8+(i*41+rank*13)%(w-16);y=30+(t*.8+i*33)%(h-40)
            rect(c,x,y,1,1,mix(s['back'],BLUE,.22))
        if rank==9:
            strength=.25 if int(t)%7==0 else .06
            rect(c,18,94,50,1,mix(s['back'],BLUE,strength))
    elif stage==4:
        # Forward progress flows in opposite directions through the paired panes.
        if rank==12:
            phase=int(t*1.3)%6
            for side,x in enumerate((20,166)):
                for i in range(min(4,max(0,phase-side))):
                    rect(c,x+9+i*18,172,12,12,mix(s['panel'],CYAN if side==0 else GREEN,.45))
            x=29+(t*27)%223
            rect(c,x,301,4,2,CYAN)
        elif rank==13:
            for i in range(5):rect(c,16+i*20,116,14,3,GREEN if int(t*1.5)%6>i else s['panel'])
        elif rank==14:
            for i in range(5):
                x=30+i*46;yy=521+round(math.sin(t*.7+i)*2)
                rect(c,x,yy,2,2,mix(CYAN,WHITE,.25))
