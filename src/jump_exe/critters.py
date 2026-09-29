"""Small, hand-clustered pixel creatures and brief reactions in the desktop world."""
import math
from .course import ROOMS
from .environment import rect,label,glow
from .desktop_style import BG,DEEP,PANEL,TEXT,WHITE,JADE,GREEN,CYAN,RED,YELLOW,BLUE,MUTED,mix

DUCK=(
    '...ddd.....',
    '..dyyyd....',
    '..dyxydd...',
    '..dyyyood..',
    '...dyyd....',
    '.ddyyyydd..',
    'dyyyyyyyyd.',
    '.dywwwyyd..',
    '..ddddd....',
    '...o.o.....',
)
PENGUIN=(
    '...gggg....',
    '..gddddg...',
    '.gdwwwwdg..',
    '.gdwxxwdg..',
    '.gdwoowdg..',
    '..gdwwdg...',
    '.gdwwwwdg..',
    'gdwwcwwwdg.',
    'gdwwwwwwdg.',
    '.gdwwwwdg..',
    '..gddddg...',
    '..oo..oo...',
)
BUG=(
    '.d...d.',
    '..rrr..',
    'drwxwrd',
    '.rrrrr.',
    'd.rrr.d',
    '..d.d..',
)
CAT=(
    '...g....g.............',
    '..gmg..gmg............',
    '..gmmggmmg............',
    '..gmwwwwmg..gggg......',
    '...gmxxmg.ggmmmmg.....',
    '....gowg.gmmmmmmmg....',
    '....gwwggmmmmmmwwg....',
    '....gwwmmmmmmmwwwg.gg.',
    '.....ggwwwwwwwwgg.gmg.',
    '......gggggggggggggg..',
)
BOT=(
    '......c..........',
    '.....ggg.........',
    '..ggggggggggg....',
    '..gwwwwwwwwwg....',
    '..gdddddddddg....',
    '..gdcdddcdddg....',
    '..gdddddddddg....',
    '..gdddcccdddg....',
    '..gdddddddddg....',
    '..gwwwwwwwwwg....',
    '.ggggggggggggg...',
    '.g..ggwwgg..g....',
    '....gddddg.......',
    '....gg..gg.......',
)
MOTH=(
    '.o...o.',
    'owwdwwo',
    '.wddd.w',
    '..wdw..',
    '...d...',
)


def creature(c,kind,x,y,t=0.,facing=1,flying=False,cold=False):
    rows={'duck':DUCK,'penguin':PENGUIN,'bug':BUG,'cat':CAT,'bot':BOT,'moth':MOTH}[kind]
    colors=dict(d=DEEP,g=MUTED,y=BLUE if cold else YELLOW,w=WHITE,x=DEEP,
                o=mix(YELLOW,RED,.3),c=CYAN,r=RED,m=mix(JADE,MUTED,.5))
    if kind=='cat':colors.update(g=DEEP,m=MUTED,w=TEXT)
    c.save();c.translate(round(x),round(y));c.scale(facing,1)
    for row,line in enumerate(rows):
        for col,ch in enumerate(line):
            if ch!='.':rect(c,col-len(line)//2,row-len(rows),1,1,colors[ch])
    if flying and kind=='duck':
        # Strong alternating wing silhouettes at the same native pixel density.
        flap=int(t*12)%3
        if flap==0:
            for i in range(4):rect(c,-2-i,-5-i,2,2,WHITE)
        elif flap==1:rect(c,-6,-5,5,2,WHITE)
        else:
            for i in range(3):rect(c,-2-i,-4+i,2,2,TEXT)
    elif kind=='penguin' and flying:
        rect(c,4,-9,2,3,JADE);rect(c,5,-10+int(t*4)%2,2,2,WHITE)
    elif kind=='cat':
        if flying:
            rect(c,-6,-6,1,1,YELLOW);rect(c,-4,-6,1,1,YELLOW)
            rect(c,7,-4-round(math.sin(t*3)),2,2,MUTED)
        elif int(t*.5)%3==1:
            rect(c,8,-15,3,1,mix(BG,BLUE,.4));rect(c,10,-14,1,1,MUTED)
            rect(c,8,-13,3,1,mix(BG,BLUE,.4))
    elif kind=='moth' and flying:
        flap=int(t*16)%2
        rect(c,-3,-4+flap,2,1,YELLOW);rect(c,2,-4+flap,2,1,YELLOW)
    elif kind=='bot':
        if int(t*1.2)%5==0:rect(c,-4,-9,7,2,DEEP)
        if flying:
            rect(c,6,-7,2,2,MUTED);rect(c,7,-9,2,3,TEXT)
            rect(c,8,-10,2,2,CYAN)
    c.restore()


def reactions(c,rank,events,t):
    for event in events:
        kind=event['kind'];x=event['x'];y=event['y'];age=event['age']
        active=event['active'];direction=event['direction']
        if kind=='duck':
            if event['perched']:
                creature(c,'duck',x,y,t,cold=rank==10)
            elif active:
                # Startle, hop, then accelerate away from the approaching player.
                fly=max(0,age-.12)
                xx=x+direction*(35*fly+24*fly*fly)
                yy=y-18*math.sin(min(1,fly)*math.pi/2)-42*fly
                creature(c,'duck',xx,yy,t,direction,True,rank==10)
        elif kind=='bugs':
            for i in range(3):
                side=-1 if i%2 else 1
                xx=x+(i-1)*10
                if active:
                    xx+=side*age*55
                    yy=y-abs(math.sin(age*16+i))*4
                else:yy=y
                if active or event['perched']:creature(c,'bug',xx,yy,t,side)
        elif kind=='penguin':
            if active:
                # A short greeting hop stays on the broad connector/keyboard.
                hop=max(0,math.sin(min(age,1)*math.pi))*9
                walk=min(age/.6,1)*max(0,min(1,event['duration']-age))
                creature(c,'penguin',x+direction*walk*8,y-hop,t,-direction,True)
            else:creature(c,'penguin',x,y,t)
        elif kind in ('cat','bot'):
            nod=round(max(0,math.sin(age*4))*2) if active and kind=='bot' else 0
            creature(c,kind,x,y-nod,t,1,active)
        elif active and kind=='diff':
            for i in range(7):
                xx=x+direction*(age*25+i*5)
                yy=y-15-age*35+age*age*22+i*4
                rect(c,xx,yy,6,3,mix(RED,TEXT,.25));rect(c,xx+1,yy+1,3,1,DEEP)
        elif active and kind=='checks':
            for i in range(5):
                xx=x+math.sin(i*2.4)*age*18
                yy=y-14-age*24+i*3
                rect(c,xx,yy,2,2,GREEN if i%2 else CYAN)
        elif active and kind=='cursor':
            xx=x+math.sin(age*2.5)*10;yy=y-28-abs(math.sin(age*3))*5
            for row,length in enumerate((1,2,3,4,5,6,4,2)):
                rect(c,xx,yy+row,length,1,TEXT)
        elif active and kind=='lamp':
            glow(c,x+8,y-19,42,YELLOW,.12*math.sin(math.pi*age/event['duration']))
        if active and event['message'] and rank!=9:
            # Small diegetic terminal notifications, kept above the encounter.
            rw=ROOMS[rank].rect[2]
            message=event['message']
            width=min(rw-12,len(message)*3.6+10)
            left=max(6,min(rw-width-6,x-width/2))
            top=max(17,y-54)
            # Reserve clear UI gutters instead of covering narrative labels or ledges.
            top={1:266,6:167,7:111,8:152,12:77,13:109}.get(rank,top)
            room=ROOMS[rank]
            positions=((xx,top+dy) for dy in (0,-16,16,-32,32,-48,48)
                       for xx in (left,6,rw-width-6))
            position=next(((xx,yy) for xx,yy in positions
                           if 17<=yy<=room.rect[3]-20 and not any(
                               xx<b.x+b.w+2 and xx+width>b.x-2
                               and yy<b.y+b.h+2 and yy+14>b.y-2
                               for b in room.blocks)),None)
            if position is None:continue
            left,top=position
            fade=min(1,age*6,(event['duration']-age)*4)
            c.set_source_rgba(*DEEP,fade*.94);c.rectangle(left,top,width,14);c.fill()
            rect(c,left,top,1,14,mix(BG,CYAN,fade))
            label(c,message,left+5,top+10,6,mix(BG,TEXT,fade))
