"""Native-pixel environmental storytelling, behind the solid jump surfaces."""
import math
from .course import ROOMS
from .environment import rect, label, glow
from .desktop_style import BG, DEEP, PANEL, TEXT, WHITE, JADE, GREEN, CYAN, MUTED, RED, YELLOW, BLUE, ACCENTS, SCENES, mix


def border(c,x,y,w,h,color):
    rect(c,x,y,w,1,color);rect(c,x,y+h-1,w,1,color)
    rect(c,x,y,1,h,color);rect(c,x+w-1,y,1,h,color)


def trace(c,points,color,packet=None):
    """Right-angle board wiring with a packet that follows the actual path."""
    length=0
    segments=[]
    for (x,y),(xx,yy) in zip(points,points[1:]):
        rect(c,min(x,xx),min(y,yy),max(1,abs(x-xx)),max(1,abs(y-yy)),color)
        size=abs(x-xx)+abs(y-yy)
        segments.append((length,size,x,y,xx,yy));length+=size
    if packet is not None and length:
        position=packet%length
        for start,size,x,y,xx,yy in segments:
            if size and start<=position<start+size:
                f=(position-start)/size
                rect(c,x+(xx-x)*f-1,y+(yy-y)*f-1,3,3,CYAN)
                break


def chip(c,x,y,w,h,color=JADE):
    for px in range(x+3,x+w-2,4):
        rect(c,px,y-2,1,h+4,mix(MUTED,color,.3))
    for py in range(y+3,y+h-2,4):
        rect(c,x-2,py,w+4,1,MUTED)
    rect(c,x,y,w,h,DEEP)
    rect(c,x+2,y+2,w-4,h-4,mix(BG,color,.2))
    rect(c,x+3,y+3,2,2,mix(TEXT,color,.3))
    for i in range(2):rect(c,x+6,y+h-5-i*3,max(1,w-11-i*2),1,mix(MUTED,BG,.5))


def note(c,x,y,rows,color=YELLOW):
    w=max(len(s) for s in rows)*3+10;h=9+len(rows)*8
    rect(c,x+2,y+2,w,h,DEEP)
    rect(c,x,y,w,h,mix(color,BG,.62))
    rect(c,x+w-5,y+h-5,5,5,mix(color,BG,.78))
    rect(c,x+w//2-4,y-2,8,4,mix(MUTED,TEXT,.2))
    for i,row in enumerate(rows):label(c,row,x+4,y+10+i*8,5,mix(TEXT,color,.25))


def lock(c,x,y,color=YELLOW):
    rect(c,x+3,y,8,2,color);rect(c,x+2,y+2,2,6,color)
    rect(c,x+10,y+2,2,6,color)
    rect(c,x,y+7,14,11,DEEP);rect(c,x+1,y+8,12,8,mix(color,MUTED,.55))
    rect(c,x+2,y+8,10,1,color);rect(c,x+6,y+10,2,4,DEEP)


def puff(c,x,y,age,color):
    # Clustered vapor, with a few isolated pixels as the plume dissipates.
    shade=mix(BG,color,max(0,.25*(1-age)))
    rect(c,x-2,y-1,5,2,shade);rect(c,x-1,y-3,3,5,shade)
    if age>.45:rect(c,x+3,y-4,1,1,shade)


def active(events,kind):
    return next((e for e in events if e['kind']==kind and e['active']),None)


def dressing(c,rank):
    """Static hardware, personal objects and wear, cached with each room."""
    w,h=ROOMS[rank].rect[2:]
    # Recessed fasteners and uneven case etching add depth without bright ledges.
    for x,y in ((5,16),(w-7,16),(5,h-8),(w-7,h-8)):
        rect(c,x,y,3,3,mix(BG,MUTED,.3));rect(c,x+1,y+1,1,1,DEEP)
    if rank==0:
        note(c,244,26,('HAND','MADE'))
        trace(c,((238,122),(245,122),(245,244),(161,244)),mix(BG,JADE,.18))
        chip(c,236,141,11,15)
        # Worn key labels and a hand-written save habit, beside the familiar editor.
        label(c,':w  :w  :w',155,232,5,mix(BG,TEXT,.45))
    elif rank==1:
        note(c,17,310,('I HAVE A','SYSTEM.'))
        border(c,13,170,96,51,mix(BG,JADE,.25))
        label(c,'incoming suggestions',18,181,5,MUTED)
        lock(c,90,190,mix(MUTED,JADE,.5))
        chip(c,17,389,15,18)
        trace(c,((24,407),(24,419),(45,419)),mix(BG,YELLOW,.3))
    elif rank==2:
        for i in range(4):
            rect(c,190+i*8,249,5,9,mix(BG,MUTED,.45))
            rect(c,191+i*8,250,2,2,MUTED)
        note(c,13,58,('TAB?',),JADE)
        trace(c,((16,162),(24,162),(24,219),(33,219)),mix(BG,JADE,.25))
        chip(c,9,180,15,20)
    elif rank==3:
        for i in range(3):
            rect(c,123+i*4,43-i*4,3,3,mix(BG,RED,.55))
        label(c,'agent loop: 99+',12,154,5,MUTED)
    elif rank==4:
        # Motherboard traces, electrolytic capacitors and copper cooling lines.
        for i in range(4):
            x=35+i*14
            rect(c,x,104,8,13,DEEP);rect(c,x+1,105,6,10,MUTED)
            rect(c,x+2,105,3,2,TEXT);rect(c,x+3,109,1,3,DEEP)
        trace(c,((250,152),(258,152),(258,328),(202,328)),mix(RED,MUTED,.65))
        trace(c,((247,155),(253,155),(253,319),(207,319)),mix(RED,BG,.5))
        chip(c,198,294,27,19,RED)
        for x in range(91,188,8):rect(c,x,346,4,3,mix(RED,BG,.5))
        label(c,'THERMAL LIMIT',100,334,5,mix(RED,TEXT,.3))
    elif rank==5:
        note(c,30,170,('IT WORKED','YESTERDAY'),RED)
        rect(c,32,350,59,27,mix(DEEP,PANEL,.2))
        border(c,32,350,59,27,mix(BG,RED,.3))
        label(c,'discard changes?',37,360,5,MUTED)
        label(c,'[ all of them ]',37,370,5,mix(TEXT,RED,.35))
    elif rank==6:
        note(c,15,63,('READ','ONLY'))
    elif rank==7:
        lock(c,111,202,mix(YELLOW,MUTED,.3))
        border(c,12,215,89,20,mix(BG,YELLOW,.22))
        label(c,'source: locked',16,228,6,MUTED)
    elif rank==8:
        for i in range(3):
            x=12+i*5;y=229+i*4
            rect(c,x,y,66,39,mix(BG,MUTED,.1))
            border(c,x,y,66,39,mix(BG,YELLOW,.25))
            for row in range(3):rect(c,x+7,y+8+row*7,39-row*6,1,mix(BG,TEXT,.25))
        label(c,'review queue',27,275,5,MUTED)
    elif rank==9:
        border(c,12,104,51,64,mix(BG,BLUE,.2))
        rect(c,15,107,45,58,mix(DEEP,BLUE,.015))
        label(c,'last session',17,117,5,mix(BG,BLUE,.5))
        for i in range(12):rect(c,14+(i*17)%50,176+(i*11)%61,1,1,mix(BG,BLUE,.16))
    elif rank==10:
        label(c,'muscle memory',20,232,5,MUTED)
    elif rank==11:
        note(c,18,147,('TOMORROW',),BLUE)
        # Tiny dust clusters and a mug ring; the desk was left in the same state.
        for i in range(14):
            rect(c,7+(i*31)%126,211-(i*7)%14,1,1,mix(BG,BLUE,.2))
        c.set_source_rgb(*mix(BG,TEXT,.2));c.set_line_width(1)
        c.arc(119,214,8,0,math.tau);c.stroke()
    elif rank==12:
        # A little backup tower behind the connected USB platform.
        rect(c,260,216,27,90,mix(DEEP,PANEL,.45))
        border(c,260,216,27,90,mix(BG,JADE,.4))
        for y in range(225,300,15):
            rect(c,264,y,19,7,DEEP);rect(c,267,y+2,12,1,mix(BG,MUTED,.7))
        trace(c,((17,302),(104,302),(104,299),(251,299),(251,221),(258,221)),mix(BG,CYAN,.22))
    elif rank==13:
        trace(c,((16,113),(16,125),(113,125),(113,212),(28,212)),mix(BG,GREEN,.35))
        chip(c,13,211,18,14,GREEN)
        label(c,'small changes',14,73,6,MUTED)
    elif rank==14:
        trace(c,((28,239),(28,225),(137,225),(137,78)),mix(BG,CYAN,.3))
        trace(c,((137,78),(138,78),(138,66),(236,66)),mix(BG,GREEN,.35))
        for i in range(3):
            rect(c,18+i*7,63,3,2,mix(GREEN,TEXT,.25))
        label(c,'you + tools',157,237,5,mix(BG,TEXT,.5))


def animate(c,rank,t,events):
    """Each stage has its own cadence: defensiveness, agitation, hesitation, quiet, flow."""
    tick=math.floor(t*8)/8
    stage=rank//3
    if stage==1:
        # Slow heat plumes, not a full-screen flashing overlay.
        for i in range(4):
            age=(tick*.22+i*.25)%1
            x,y={3:(123,132),4:(137,178),5:(90,418)}[rank]
            puff(c,x+i*3+math.sin(tick+i)*3,y-age*32,age,mix(RED,TEXT,.45))
    elif stage==3:
        w,h=ROOMS[rank].rect[2:]
        for i in range(9):
            x=8+(i*37+rank*9)%(w-16)
            y=23+(tick*1.7+i*29)%(h-36)
            rect(c,x,y,1,1,mix(BG,BLUE,.12))
    if rank==0:
        screen=mix(DEEP,BG,.5)
        rect(c,21,190,200,13,screen)
        phrase='# all me.  :w'
        label(c,phrase[:min(len(phrase),int(tick*4)%24)],22,198,7,JADE)
        event=active(events,'ghost')
        if event:
            age=event['age']
            rect(c,23,207,197,12,mix(BG,JADE,.15))
            label(c,'suggestion: let me help',27,216,6,mix(TEXT,JADE,.4))
            if age>1.4:
                rect(c,119,207,101,12,PANEL)
                label(c,'no thanks.',127,216,6,TEXT)
    elif rank==1:
        phase=tick%7
        x=19+min(phase*16,51)
        if phase<5:
            rect(c,x,190,25,17,mix(BG,JADE,.3))
            for i in range(3):rect(c,x+3,194+i*4,18-i*4,1,MUTED)
        if phase>3:
            for i in range(7):
                rect(c,75+i,195+i,2,2,TEXT);rect(c,81-i,195+i,2,2,TEXT)
    elif rank==2:
        rect(c,61,205,99,24,DEEP)
        phrase='hello, world'
        count=min(len(phrase),int(tick*5)%23)
        label(c,phrase[:count],63,214,6,mix(JADE,TEXT,.4))
        label(c,'[tab] maybe later',63,226,5,MUTED)
        if count==len(phrase):rect(c,62,210,79,1,mix(BG,MUTED,.7))
    elif rank==3:
        rect(c,10,88,119,42,BG)
        for i in range(1+int(tick*.8)%3):
            x=12+i*8;y=89+i*6
            rect(c,x,y,89,23,mix(DEEP,RED,.05))
            border(c,x,y,89,23,mix(BG,RED,.6))
            label(c,'fix failed again',x+5,y+11,6,mix(TEXT,RED,.35))
            rect(c,x+6,y+16,64,2,mix(BG,RED,.35))
            rect(c,x+6,y+16,12+(int(tick*16)%45),2,RED)
    elif rank==4:
        glow(c,139,195,101,RED,.025+.015*math.sin(tick*.8))
        # Irregular warning LEDs, and a visible spark only after a nearby landing.
        event=active(events,'fan')
        for i in range(4):
            rect(c,202+i*5,317,2,2,RED if int(tick*3+i)%5<2 else DEEP)
        if event and event['age']<1.1:
            for i in range(5):
                age=event['age'];x=250+math.sin(i*4)*age*11;y=166-age*19+i*3
                rect(c,x,y,1,2,YELLOW if i%2 else RED)
    elif rank==5:
        age=tick%6
        if age<3:
            x=75+math.sin(age)*8;y=382+age*age*3
            rect(c,x,y,9,10,mix(TEXT,BG,.4))
            for i in range(3):rect(c,x+2,y+2+i*2,5,1,mix(RED,BG,.25))
        if active(events,'diff'):
            label(c,'REVERTED',35,345,7,RED)
    elif rank==6:
        event=active(events,'cursor')
        if event:
            y=108
            rect(c,78,y,129,13,mix(DEEP,YELLOW,.08))
            label(c,'allow once' if event['age']>1.6 else 'checking scope...',83,y+9,6,YELLOW)
        phase=tick%9
        rect(c,86,190,22,16,mix(BG,YELLOW,.05))
        for i in range(3):rect(c,89+i*6,198,2,2,YELLOW if phase>i*2 else MUTED)
    elif rank==7:
        progress=1 if active(events,'checks') else min(.66,(tick%9)/7)
        for i in range(14):
            rect(c,17+i*6,180,3,2,(GREEN if progress==1 else YELLOW)
                 if i/14<progress else mix(BG,MUTED,.4))
        # A moving audit marker keeps running into the permission boundary.
        rect(c,8,91+min(4,int(tick)%7)*12,2,5,YELLOW)
    elif rank==8:
        row=int(tick*.65)%12
        for i in range(12):
            x=137;y=93+i*13
            border(c,x,y,5,5,mix(BG,YELLOW,.3))
            if i<row:rect(c,x+1,y+1,3,3,mix(GREEN,BG,.4))
        if active(events,'cursor'):
            rect(c,193,249,66,16,mix(BG,YELLOW,.2))
            label(c,'ONE MORE...',199,260,7,YELLOW)
    elif rank==9:
        event=active(events,'wake')
        strength=math.sin(math.pi*event['age']/event['duration']) if event else .1
        rect(c,18,147,39,1,mix(BG,BLUE,strength*.65))
        if event:
            label(c,'anyone?',18,139,6,mix(BG,BLUE,strength))
    elif rank==10:
        rect(c,59,76,87,20,SCENES[3]['back'])
        phrase='how do I...'
        phase=tick%12
        count=max(0,min(len(phrase),int(phase*2) if phase<7 else int((12-phase)*2.3)))
        label(c,phrase[:count],60,90,10,mix(BLUE,MUTED,.5))
        if int(tick)%2:rect(c,60+count*6,92,5,1,BLUE)
        for i in range(5):
            rect(c,192+i*10,241-i%2,1,1,mix(TEXT,MUTED,.5))
    elif rank==11:
        rect(c,12,14,98,24,SCENES[3]['back'])
        label(c,'03:17' if int(tick)%2 else '03 17',15,35,22,BLUE)
        rect(c,24,95,99,15,mix(DEEP,SCENES[3]['back'],.5))
        phrase='// tomorrow'
        phase=tick%14
        count=int(min(11,phase*1.8)) if phase<8 else max(0,int((14-phase)*1.8))
        label(c,phrase[:count],29,107,6,mix(BLUE,MUTED,.4))
        if int(tick)%3==0:rect(c,29+count*3.6,101,3,7,BLUE)
    elif rank==12:
        phase=tick%10
        panel=mix(DEEP,BG,.5)
        for x,w in ((17,101),(160,120)):rect(c,x,99,w,50,panel)
        rows=(('  keep it small',CYAN),('  show the diff',TEXT),('  I will review',TEXT))
        for i,(word,color) in enumerate(rows):
            label(c,word[:max(0,min(len(word),int(phase*8-i*12)))],19,114+i*15,6,mix(BG,color,.7))
        for i,word in enumerate(('  reading files','  writing tests','  tests passed')):
            if phase>2+i:
                label(c,word,164,114+i*15,6,mix(BG,GREEN,.8))
                rect(c,272,108+i*15,3,3,GREEN if phase>4+i else YELLOW)
        if phase>7:label(c,'> looks good.',19,221,6,CYAN)
        trace(c,((17,302),(104,302),(104,299),(251,299),(251,221),(258,221)),
              mix(BG,CYAN,.22),tick*36)
        for i in range(5):rect(c,282,228+i*15,1,2,GREEN if int(tick*2+i)%4 else CYAN)
    elif rank==13:
        phase=tick%10
        count=8 if active(events,'checks') else min(8,1+int(phase*2))
        rect(c,12,79,111,27,mix(SCENES[4]['panel'],GREEN,.18))
        label(c,f'{count} / 8',15,100,24,GREEN)
        trace(c,((16,113),(16,125),(113,125),(113,212),(28,212)),mix(BG,GREEN,.35),tick*23)
        for i in range(4):
            if count>i*2:
                rect(c,117,161+i*14,3,3,GREEN)
    elif rank==14:
        trace(c,((28,239),(28,225),(137,225),(137,78),(138,78),(138,66),(236,66)),
              mix(BG,CYAN,.3),tick*30)
        # A calm cadence of reviewed work; success is shared, not an endless alert.
        for i in range(3):
            age=(tick*.15+i/3)%1
            rect(c,152+i*14,224-age*23,1,1,mix(BG,CYAN,(1-age)*.65))
        if active(events,'penguin'):
            for i in range(5):
                x=208+i*9;y=24+math.sin(tick+i)*3
                rect(c,x,y,1,3,mix(CYAN,WHITE,.4));rect(c,x-1,y+1,3,1,mix(CYAN,WHITE,.4))


def surface_lights(c,rank,t):
    """Small inset indicators; the bright collision edges are never covered."""
    stage=rank//3
    for i,b in enumerate(ROOMS[rank].blocks):
        if b.material not in ('board','case','crt','cable','battery') or b.w<20:
            continue
        x=b.x+b.w-6;y=b.y+b.h-5
        phase=int(t*(3 if stage==1 else 1)+i)%6
        color=(JADE,RED,YELLOW,BLUE,CYAN)[stage]
        on=phase<3 if stage!=3 else phase==0
        rect(c,x,y,2,2,color if on else mix(BG,MUTED,.25))
