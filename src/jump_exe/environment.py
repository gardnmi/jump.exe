"""Small environmental stories and animation, clipped to the native game windows."""
import math
import cairo
from .character import guide
from .story import objects
from .course import GUIDE_POINT, BLACK_PILL, WHITE_PILL
from .desktop_style import BG,DEEP,PANEL,TEXT,WHITE,JADE,GREEN,CYAN,MUTED,YELLOW,RED,BLUE,FONT,mix

CREAM = TEXT
DARK = DEEP
SAGE = JADE


def rect(c,x,y,w,h,color):
    c.set_source_rgb(*color)
    c.rectangle(round(x),round(y),round(w),round(h))
    c.fill()


def label(c,value,x,y,size=4,color=CREAM):
    c.set_source_rgb(*color)
    c.select_font_face(FONT,0,0)
    c.set_font_size(size)
    c.move_to(round(x),round(y))
    c.show_text(value)


def glow(c,x,y,r,color,alpha=.15):
    gradient = cairo.RadialGradient(x,y,0,x,y,r)
    gradient.add_color_stop_rgba(0,*color,alpha)
    gradient.add_color_stop_rgba(1,*color,0)
    c.set_source(gradient)
    c.rectangle(x-r,y-r,r*2,r*2)
    c.fill()


def capsule(c,x,y,white,t):
    y += round(math.sin(t*2)*1.5)
    color = (1.,.95,.76) if white else (.12,.12,.15)
    glow(c,x,y,28 if white else 13,color,.3 if white else .45)
    rect(c,x-5,y-4,10,8,(.4,.43,.44) if not white else (.55,.6,.48))
    rect(c,x-7,y-2,14,4,color)
    rect(c,x-4,y-4,8,8,color)
    rect(c,x,y-3,1,6,(.7,.72,.61) if white else (.03,.03,.045))
    rect(c,x-4,y-3,3,1,(1.,1.,.92) if white else (.28,.3,.31))
    if white:
        for i in range(6):
            a=t*.45+i*math.tau/6
            rect(c,x+math.cos(a)*18,y+math.sin(a)*12,1,1,CREAM)


def object_art(c,kind,x,y,value,t,level):
    if kind == 'crt':
        tint = (.43,.42,.32) if level<3 else (.25,.31,.34) if level==3 else (.64,.64,.46)
        rect(c,x-11,y-19,22,15,DARK)
        rect(c,x-10,y-18,20,13,tint)
        rect(c,x-8,y-16,15,9,(.04,.09,.075))
        rect(c,x-3,y-4,6,3,tint)
        rect(c,x-7,y-1,14,1,tint)
        live = value not in ('offline','sleep')
        color = (.93,.35,.18) if value=='error' else (.58,.75,.45)
        if live:
            glow(c,x,y-10,19,color,.16)
            for row in range(3):
                length = (int(t*2)+row*3)%9+2
                rect(c,x-6,y-14+row*2,length,1,color)
        elif value=='sleep' and int(t)%5==0:
            rect(c,x-6,y-10,2,1,(.31,.49,.51))
        rect(c,x+8,y-7,1,1,color if live and int(t*2)%2 else (.18,.23,.17))
    elif kind == 'keyboard':
        tint = CREAM if value in ('manual','dust') else MUTED
        rect(c,x-14,y-8,28,8,DEEP)
        rect(c,x-13,y-7,26,5,mix(MUTED,DEEP,.4))
        rect(c,x-13,y-8,26,1,tint)
        for row in range(2):
            for col in range(8):
                if value=='broken' and col%3==1:
                    continue
                rect(c,x-12+col*3,y-6+row*2,2,1,tint)
        rect(c,x-12,y-6,2,1,CYAN)
        rect(c,x-4,y-2,9,1,tint)
        rect(c,x+11,y-6,1,1,JADE)
        if value=='broken':
            rect(c,x+14,y-1,2,1,CREAM)
            rect(c,x+18,y-2,2,1,CREAM)
    elif kind == 'chair':
        tint=mix(JADE,MUTED,.7)
        rect(c,x-7,y-25,15,14,DEEP)
        rect(c,x-6,y-24,12,12,tint)
        rect(c,x-6,y-24,12,1,mix(TEXT,tint,.55))
        for row in range(3):
            for col in range(3):rect(c,x-4+col*3,y-22+row*3,1,1,DEEP)
        rect(c,x-5,y-28,11,3,tint)
        rect(c,x-7,y-12,18,4,DEEP)
        rect(c,x-6,y-12,16,2,tint)
        rect(c,x+9,y-16,2,6,tint)
        rect(c,x+7,y-17,7,2,MUTED)
        rect(c,x,y-8,3,5,MUTED)
        rect(c,x-7,y-3,18,1,MUTED)
        for dx in (-8,8):
            rect(c,x+dx,y-2,4,2,DEEP)
            rect(c,x+dx+1,y-2,2,1,tint)
    elif kind == 'lamp':
        tint=mix(MUTED,TEXT,.3)
        rect(c,x-6,y-3,14,3,DEEP)
        rect(c,x-5,y-3,12,1,tint)
        rect(c,x,y-17,2,14,tint)
        for i in range(7):rect(c,x+i,y-18-i,2,2,tint)
        rect(c,x-1,y-19,4,4,MUTED)
        rect(c,x,y-19,1,1,TEXT)
        rect(c,x+3,y-29,13,5,DEEP)
        rect(c,x+4,y-29,11,3,tint)
        rect(c,x+2,y-26,15,2,JADE)
        rect(c,x+4,y-24,11,1,YELLOW)
        glow(c,x+8,y-14,24,YELLOW,.13+math.sin(t*2)*.015)
    elif kind == 'coffee':
        rect(c,x-6,y-11,12,10,DEEP)
        rect(c,x-5,y-10,10,9,TEXT)
        rect(c,x-4,y-10,8,2,DEEP)
        rect(c,x-4,y-7,1,5,WHITE)
        rect(c,x+3,y-8,2,6,MUTED)
        rect(c,x-1,y-6,2,2,JADE)
        rect(c,x+5,y-8,3,5,TEXT)
        rect(c,x+5,y-7,2,3,DEEP)
        rect(c,x-4,y-1,9,1,MUTED)
        if value!='cold':
            for i in range(2):
                yy=y-13-(t*4+i*5)%10
                rect(c,x-2+i*3,yy,1,2,mix(BG,TEXT,.3))
    elif kind == 'plant':
        tint=MUTED if value=='wilt' else GREEN
        rect(c,x-6,y-8,12,7,DEEP)
        rect(c,x-5,y-7,10,5,mix(JADE,TEXT,.3))
        rect(c,x-5,y-8,10,2,TEXT);rect(c,x-4,y-6,1,4,WHITE)
        rect(c,x+3,y-6,2,5,MUTED);rect(c,x-3,y-1,7,1,DEEP)
        sway=round(math.sin(t*.9+x))
        rect(c,x+sway,y-23,1,15,tint)
        for dx,dy,side in ((-7,-18,-1),(1,-23,1),(-5,-26,-1),(2,-14,1)):
            rect(c,x+dx+sway,y+dy,5,3,mix(tint,DEEP,.3))
            rect(c,x+dx+sway+1,y+dy-1,3,2,tint)
            rect(c,x+dx+sway+(0 if side<0 else 2),y+dy,2,1,mix(tint,TEXT,.45))
    elif kind == 'books':
        for i,(width,color) in enumerate(((24,JADE),(20,MUTED),(22,YELLOW))):
            xx=x-width/2+(i%2)*2;yy=y-5-i*5
            rect(c,xx-1,yy-1,width+2,6,DEEP)
            rect(c,xx,yy,width,4,mix(color,DEEP,.3))
            rect(c,xx+4,yy+1,width-5,2,TEXT)
            rect(c,xx+5,yy+2,width-7,1,mix(TEXT,MUTED,.5))
            rect(c,xx,yy,2,4,color)
    elif kind == 'notepad':
        rect(c,x-9,y-16,19,16,DEEP)
        rect(c,x-8,y-15,16,13,mix(TEXT,MUTED,.2))
        rect(c,x-7,y-14,14,1,WHITE)
        for i in range(3):
            yy=y-11+i*3
            rect(c,x-5,yy,2,2,JADE if i<2 else YELLOW)
            rect(c,x-1,yy,6-i,1,MUTED)
        for i in range(4):rect(c,x-6+i*4,y-17,1,4,DEEP)
        rect(c,x+10,y-14,2,12,YELLOW);rect(c,x+10,y-2,1,2,TEXT)
    elif kind == 'bin':
        rect(c,x-8,y-18,16,18,DEEP)
        rect(c,x-7,y-17,14,2,MUTED)
        rect(c,x-6,y-15,12,13,PANEL)
        for yy in range(-13,-3,3):
            for xx in range(-4,5,3):rect(c,x+xx,y+yy,1,1,MUTED)
        for dx,dy in ((-4,-20),(2,-23),(4,-18)):
            rect(c,x+dx-2,y+dy,5,6,mix(TEXT,DEEP,.22))
            rect(c,x+dx-1,y+dy+2,3,1,RED)
    elif kind == 'printer':
        rect(c,x-19,y-20,38,19,DEEP)
        rect(c,x-18,y-18,36,14,mix(MUTED,PANEL,.45))
        rect(c,x-17,y-20,34,3,MUTED)
        rect(c,x-17,y-19,33,1,mix(TEXT,MUTED,.5))
        rect(c,x-12,y-28,24,11,DEEP)
        rect(c,x-10,y-27,20,10,TEXT)
        for i in range(3):rect(c,x-7,y-25+i*3,13-i*3,1,MUTED)
        rect(c,x-13,y-11,25,4,DEEP)
        feed=int(t*3)%6
        rect(c,x-9,y-8,18,4+feed,TEXT)
        for i in range(2):rect(c,x-6,y-6+i*3,11,1,RED if value=='error' else JADE)
        rect(c,x+13,y-15,2,2,RED if value=='error' else GREEN)
        rect(c,x-15,y-3,4,3,DEEP);rect(c,x+11,y-3,4,3,DEEP)
    elif kind in ('paper','calendar','box'):
        if kind=='box':
            rect(c,x-12,y-15,24,15,(.29,.26,.18))
            rect(c,x-12,y-15,24,2,(.46,.4,.26))
            rect(c,x-2,y-15,4,15,(.4,.34,.22))
            label(c,value,x-11,y-5,3)
        else:
            rect(c,x-10,y-15,20,15,(.62,.56,.41))
            rect(c,x-9,y-14,18,12,(.77,.7,.53))
            if kind=='calendar':
                rect(c,x-9,y-14,18,3,(.36,.23,.18))
                label(c,value,x-5,y-4,7,(.22,.22,.18))
            else:
                label(c,value,x-9,y-8,3,(.31,.21,.16))
                for i in range(2):
                    rect(c,x-7,y-6+i*2,11-i*3,1,(.54,.47,.35))
    elif kind=='cable':
        c.set_line_width(1)
        c.set_source_rgb(.38,.39,.29)
        c.move_to(x-17,y-2)
        c.curve_to(x-4,y-12,x+3,y+3,x+12,y-5)
        c.stroke()
        rect(c,x+12,y-6,4,3,CREAM if value=='joined' else (.3,.32,.31))
        if value=='joined':
            rect(c,x+16,y-6,4,3,SAGE)
    elif kind=='vent':
        rect(c,x-10,y-7,20,7,(.2,.18,.16))
        for i in range(6):
            rect(c,x-8+i*3,y-5,1,4,(.7,.26,.12))
        for i in range(4):
            life=(t*.7+i*.25)%1
            c.set_source_rgba(.55,.4,.28,(1-life)*.3)
            c.rectangle(round(x-5+i*3+math.sin(t+i)*2),round(y-8-life*24),3,3)
            c.fill()
    elif kind=='beacon':
        rect(c,x-3,y-10,6,10,(.25,.22,.16))
        color=(.98,.31,.1) if int(t*2)%2 else (.37,.16,.09)
        rect(c,x-2,y-12,4,5,color)
        glow(c,x,y-9,16,color,.18)


def ambience(c,w,h,rank,level,t):
    # Quiet screen glow and desk dust; motion belongs to each app/hardware scene.
    if rank in (0,11):
        for i in range(5):
            x=(i*43+t*2+rank*5)%w
            y=(i*31+17+math.sin(t+i)*3)%h
            rect(c,x,y,1,1,mix(BG,TEXT,.17))
    if rank in (2,12,14):
        glow(c,w*.5,h*.5,w*.6,CYAN,.025)


def props(c,rank,level,t,accepted=False,talking=False,celebrating=False):
    for kind,x,y,value in objects(rank):
        object_art(c,kind,x,y,value,t,level)
    if rank==0:
        _,x,y=BLACK_PILL
        rect(c,x-9,y+12,18,3,(.18,.19,.17))
        capsule(c,x,y,False,t)
        guide(c,*GUIDE_POINT[1:],t,talking)
    elif rank==14:
        _,x,y=WHITE_PILL
        if not celebrating:rect(c,x-15,y-3,30,3,(.68,.67,.49))
        if not accepted:
            capsule(c,x,y-16,True,t)
        elif not celebrating:
            glow(c,x,y-16,65,(1.,.93,.62),.3)
            for i in range(10):
                rect(c,x-26+(i*17)%53,y-(t*9+i*13)%40,1,1,CREAM)
