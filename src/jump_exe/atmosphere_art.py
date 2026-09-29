"""Native-pixel environmental motion. Always clipped to a real game window."""
import math

from .atmosphere import SCREENS, RESIDENTS, pulse
from .course import ROOMS
from .character import frame
from .critters import creature
from .environment import rect, label
from .desktop_style import DEEP, TEXT, WHITE, MUTED, JADE, RED, YELLOW, BLUE, CYAN, GREEN, mix


# Clear glass inside the existing app previews, away from solid terrain.
BUILD_AREAS = {12:(167,153,90),13:(12,78,110),14:(154,378,94)}


def alpha_rect(c,x,y,w,h,color,alpha):
    c.set_source_rgba(*color,max(0,min(1,alpha)))
    c.rectangle(round(x),round(y),round(w),round(h));c.fill()


def silhouette(c,x,y,pose,facing,color,alpha):
    c.save();c.translate(round(x),round(y));c.scale(facing,1)
    c.set_source_rgba(*color,alpha)
    c.mask_surface(frame(pose),-20,-36)
    c.restore()


def conduit(c,points,color,age):
    # A single packet traverses the complete orthogonal path, not a flashing line.
    lengths=[abs(x2-x1)+abs(y2-y1) for (x1,y1),(x2,y2) in zip(points,points[1:])]
    distance=age*100
    for ((x1,y1),(x2,y2)),length in zip(zip(points,points[1:]),lengths):
        alpha_rect(c,min(x1,x2),min(y1,y2),max(1,abs(x2-x1)),max(1,abs(y2-y1)),color,.2)
        if 0<=distance<=length:
            t=distance/max(1,length)
            rect(c,x1+(x2-x1)*t-1,y1+(y2-y1)*t-1,3,3,color)
        distance-=length


def behind(c,rank,fx):
    if not fx:return
    t=fx['time'];stage=rank//3;w,h=ROOMS[rank].rect[2:]
    sx,sy,sw,sh=SCREENS[rank];hero=fx['hero']
    wake=fx['wake']
    if 0<=wake<6:
        brightness=pulse(wake,6)
        alpha_rect(c,sx+1,sy+13,sw-2,sh-14,(JADE,RED,YELLOW,BLUE,CYAN)[stage],brightness*.09)
        # A boot cursor opens into a small status line on the existing glass.
        status=('AI: disabled','retry queued','scope checked','...','worker online')[stage]
        if wake<.7:status='_'
        elif stage==0 and wake<1.5:status='assistant?'
        width=min(sw-4,len(status)*3+8)
        alpha_rect(c,sx+2,sy+sh-12,width,10,DEEP,.9)
        label(c,status,sx+5,sy+sh-5,5,mix(DEEP,TEXT,brightness*.75))
    if stage==0 and fx['echo']:
        echo=fx['echo'];age=t-echo['start'];a=max(0,age-.08)
        x=echo['x']+echo['direction']*a*72
        y=echo['y']-145*a+145*a*a
        opacity=.19*max(0,1-age/1.2)
        silhouette(c,x,y,'rise' if a<.5 else 'fall',echo['direction'],JADE,opacity)
        for i in range(5):
            q=max(0,a-i*.045)
            alpha_rect(c,echo['x']+echo['direction']*q*72,echo['y']-145*q+145*q*q,1,1,JADE,opacity)
        label(c,'suggestion',max(4,min(w-43,x-18)),max(20,y-36),5,mix(DEEP,JADE,opacity*2))
    elif stage==1:
        vx,vy=fx['vent_origin'];heat=pulse(fx['vent'],2.8)
        if heat:
            for i in range(6):
                a=(fx['vent']+i*.21)%1.5
                px=vx+a*37;py=vy-12-a*17+math.sin(t*5+i)*3
                alpha_rect(c,px,py,7,2,RED,heat*(1-a/1.5)*.17)
                alpha_rect(c,px+3,py-2,5,1,TEXT,heat*(1-a/1.5)*.12)
            for i in range(3):
                rect(c,vx-7+i*5,vy+3,3,1,mix(MUTED,RED,heat*.65))
        arc=pulse(fx['arc'],.65)
        if arc:
            # Route the discharge along a cable beside the housing.
            x=w-10
            for i in range(11):
                xx=x+(-1 if i%2 else 1)*(2+i%3)
                yy=max(20,min(h-18,(hero['y']-45 if hero else h*.5)))+i*3
                alpha_rect(c,xx,yy,3,2,mix(RED,WHITE,.55),arc*.8)
                alpha_rect(c,xx-2,yy-1,7,4,RED,arc*.08)
        if 0<=fx['shake']<.5:
            for i in range(5):
                x=sx+3+i*(sw-8)//5;y=sy+2
                shift=round(math.sin(fx['shake']*35+i)*(1-fx['shake']*2))
                rect(c,x+shift,y,3,3,MUTED);rect(c,x+shift+1,y+1,1,1,DEEP)
    elif stage==2 and hero:
        age=fx['scan'];x=hero['x'];y=hero['y']
        if 0<=age<1.4:
            yy=y-31+age/1.4*31
            alpha_rect(c,max(3,x-23),yy,min(46,w-6),1,YELLOW,.5)
            for side in (-1,1):
                rect(c,x+side*23,y-31,1,31,mix(DEEP,YELLOW,.5))
        elif 1.4<=age<3.2:
            x=max(4,min(w-52,x-24));y=max(23,y-43)
            alpha_rect(c,x,y-8,49,12,DEEP,.8)
            label(c,'APPROVED',x+3,y,6,mix(DEEP,GREEN,min(1,(3.2-age)*2)))
    elif stage==3:
        # Glass dims on approach; the cursor stops blinking, then returns slowly.
        age=fx['wake']
        darkness=.26+pulse(age,3)*.3
        alpha_rect(c,sx+1,sy+13,sw-2,sh-14,DEEP,darkness)
        reflected=fx['reflection']
        if reflected:
            c.save();c.rectangle(sx+2,sy+14,sw-4,sh-16);c.clip()
            x=sx+sw-(reflected['x']-sx)
            silhouette(c,x,reflected['y'],reflected['pose'],-reflected['facing'],BLUE,.14)
            for yy in range(sy+15,sy+sh-2,3):
                alpha_rect(c,sx+2,yy,sw-4,1,DEEP,.6)
            c.restore()
        if not 0<=age<2 and int(t*.65)%3==0:
            rect(c,sx+7,sy+sh-19,4,1,mix(DEEP,BLUE,.45))
    elif stage==4:
        age=fx['build']
        if 0<=age<7:
            # A tiny application takes shape inside the agent's display.
            x,y,width=BUILD_AREAS[rank]
            alpha_rect(c,x,y,width,40,DEEP,.9)
            label(c,'build: '+('ready' if age>2.1 else 'working'),x+3,y+7,5,CYAN)
            count=min(3,int(age*1.5))
            rect(c,x+3,y+12,width-6,2,mix(JADE,TEXT,.2))
            for i in range(count):
                xx=x+4+i*(width-8)//3
                rect(c,xx,y+18,(width-12)//3,13,mix(DEEP,CYAN,.38))
                rect(c,xx+2,y+20,max(2,(width-24)//3),2,GREEN)
                rect(c,xx+2,y+25,max(2,(width-30)//3),1,TEXT)
            rect(c,x+3,y+35,round((width-6)*min(1,age/2.1)),1,GREEN)
            source=hero or dict(x=sx,y=sy+sh)
            conduit(c,[(source['x'],source['y']-2),(w-7,source['y']-2),
                       (w-7,sy+sh//2),(sx+sw,sy+sh//2)],CYAN,age)
        for i,b in enumerate(ROOMS[rank].blocks):
            glow=pulse(age-i*.13,1.3)
            if glow:alpha_rect(c,b.x+b.w-5,b.y-3,2,2,CYAN,glow)


def front(c,rank,fx):
    if not fx:return
    t=fx['time'];stage=rank//3
    palette=(JADE,RED,YELLOW,BLUE,CYAN)
    for p in fx['particles']:
        x,y=p['x'],p['y'];alpha=min(.8,p['life']*1.8)
        if p['kind']=='paper':
            tilt=round(math.sin(t*6+x)*2) if not p['settled'] else 0
            alpha_rect(c,x-3,y-5,6,4,TEXT,alpha*.75)
            alpha_rect(c,x-2,y-4+tilt//2,3,1,palette[stage],alpha)
        elif p['kind']=='screw':
            alpha_rect(c,x,y-2,3,2,MUTED,alpha)
            alpha_rect(c,x+1,y-3,1,4,TEXT,alpha)
        elif p['kind']=='text':
            label(c,p['glyph'],x,y,5,mix(DEEP,JADE,alpha*.65))
        elif p['kind']=='check':
            for dx,dy in ((0,-2),(1,-1),(2,-2),(3,-3),(4,-4)):
                alpha_rect(c,x+dx,y+dy,1,1,CYAN,alpha*.7)
        else:
            color=mix(MUTED,BLUE,.45) if stage==3 else mix(TEXT,palette[stage],.35)
            alpha_rect(c,x,y-1,2 if stage==3 else 1,1,color,alpha*.5)
    if rank in RESIDENTS:
        sx,sy,sw,sh=SCREENS[rank];age=fx['moth'];x=sx+sw-8;y=sy+sh-2
        if 0<=age<4:
            # Startle, circle the warm glass, then tuck back into its corner.
            amount=math.sin(math.pi*age/4)
            x-=amount*(13+7*math.sin(age*4));y-=amount*(18+5*math.cos(age*6))
        creature(c,'moth',x,y,t,1,0<=age<4)
