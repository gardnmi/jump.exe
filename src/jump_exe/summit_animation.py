"""The white-pill pickup performed on the real summit, inside its native pixels."""
import math
from .character import draw,guide
from .critters import creature
from .environment import rect,label,object_art,capsule,glow
from .desktop_style import DEEP,PANEL,TEXT,WHITE,MUTED,JADE,GREEN,CYAN,YELLOW,mix
from .ending import PROJECT_PROMPT,AGENT_REPLY,in_world
from .course import ROOMS


def smooth(value):
    value=max(0,min(1,value))
    return value*value*(3-2*value)


def key_depth(t):
    return 3*smooth((t-1.35)/.22)*(1-smooth((t-2.05)/.3))


def type_line(c,line,x,y,t,start,size=7,color=TEXT,speed=35):
    if t<start:return
    visible=line[:int((t-start)*speed)]
    label(c,visible,x,y,size,color)


def press_enter(c,foreground,background,t):
    depth=round(key_depth(t))
    if not depth:return
    b=next(b for b in ROOMS[14].blocks if b.name=='summit')
    c.save();c.rectangle(b.x,b.y,b.w,b.h);c.clip()
    c.set_source_surface(background,0,0);c.paint()
    c.rectangle(b.x,b.y+depth,b.w,b.h-depth);c.clip()
    c.set_source_surface(foreground,0,depth);c.paint()
    c.restore()


def pulse(c,rank,t):
    if t<1.6 or rank<12:return
    room=ROOMS[rank]
    for i,b in enumerate(room.blocks):
        # Highlight the visible hardware in succession, then let it settle.
        age=t-1.6-i*.10-(14-rank)*.35
        if 0<age<1.4:
            amount=math.sin(age/1.4*math.pi)
            color=mix(JADE,WHITE,amount)
            rect(c,b.x,b.y,b.w,1,color)
            rect(c,b.x,b.y,1,b.h,color)
            if b.w>40:
                x=b.x+int((age/1.4)*max(0,b.w-8))
                rect(c,x,b.y+3,6,2,CYAN)
    if rank in (12,13) and t>2.3:
        rect(c,8,18,room.rect[2]-16,14,DEEP)
        label(c,'ALL CHECKS PASS',14,28,7,CYAN)


def celebration(c,t):
    if t<2.15:return
    age=t-2.15
    if age<3:
        for i in range(24):
            a=i*2.39996;speed=18+i%6*5
            x=236+math.cos(a)*speed*age
            y=40-abs(math.sin(a))*speed*age+18*age*age
            if 12<x<284 and 14<y<317:
                color=WHITE if i%3==0 else CYAN if i%3==1 else YELLOW
                if i%4==0:label(c,'{}',x,y,5,color)
                else:rect(c,x,y,2,2,color)
    # The opening duck makes one flyby. The terminal helper and penguin stay
    # on real landing surfaces, waving and hopping rather than blocking them.
    if age<3.1:
        creature(c,'duck',-8+age*106,91-12*math.sin(age*2),t,1,True)
    creature(c,'bot',151,112-round(max(0,math.sin(age*5))*4),t,1,True)
    creature(c,'penguin',48,218-round(max(0,math.sin(age*4))*7),t,1,True)
    guide(c,248,288,t,True)


def terminal(c,t):
    if t<4.5:return
    # Occupy the clear space between CHECKS PASS and SHIFT, not their edges.
    x,y,w,h=18,134,246,78
    rect(c,x,y,w,h,CYAN);rect(c,x+1,y+1,w-2,h-2,DEEP)
    rect(c,x+2,y+2,w-4,10,PANEL)
    label(c,'[+]  agent / one small project',x+6,y+9,5,JADE)
    type_line(c,'you> '+PROJECT_PROMPT,x+8,y+26,t,4.7,7,WHITE)
    type_line(c,'agent> '+AGENT_REPLY,x+8,y+41,t,5.95,6,CYAN)
    type_line(c,'[+] hand-assembling the borrow checker...',x+8,y+58,t,7.25,6,TEXT,44)
    if t>8.35:
        label(c,'estimated time: yes',x+8,y+70,6,YELLOW)
    elif int(t*3)%2:rect(c,x+8,y+63,4,6,TEXT)


def draw_world(c,rank,ending,foreground,background):
    if not in_world(ending) or rank<12:return
    t=ending['age']
    pulse(c,rank,t)
    if rank!=14:return
    press_enter(c,foreground,background,t)
    x=ending.get('hero_x',236.)
    foot=38+round(key_depth(t))
    pose='charge' if 1.3<t<2.2 or 4.1<t<4.55 else 'idle'
    draw(c,x,foot,1,1,pose,t)
    if t<1.4:
        amount=smooth(t/1.25)
        # A raised sleeve and hand meet the capsule without replacing the sprite.
        rect(c,x+5,foot-13,5,2,JADE);rect(c,x+9,foot-14,2,3,TEXT)
        px=236+(x+10-236)*amount;py=22+(foot-13-22)*amount
        c.save();c.translate(round(px),round(py));scale=max(.05,1-smooth((t-1.0)/.4))
        c.scale(scale,scale);capsule(c,0,0,True,t);c.restore()
    if .8<t<3:
        glow(c,x,foot-16,18,CYAN,.16*(1-abs(t-1.9)/1.1))
        rect(c,x-2,foot-20,1,8,CYAN)
        rect(c,x+2,foot-23,2,1,WHITE)
    if t>=4.4:
        object_art(c,'keyboard',198,38,'manual',t,4)
        object_art(c,'coffee',282,38,'',t,4)
    terminal(c,t)
    celebration(c,t)
