"""Omarchy-inspired desktop scenes: real coding situations, hardware and software.

Scenes are drawn at the course's native pixel scale. Text stays legible in tall
windows; no stretched illustration or scenery atlas is used.
"""
import math
from .course import ROOMS
from .environment import rect, label, glow
from .desktop_style import BG, DEEP, PANEL, MUTED, TEXT, WHITE, JADE, GREEN, CYAN, RED, YELLOW, PINK, BLUE, ACCENTS, mix
from .world_details import dressing, animate, surface_lights
from . import stage_scenes


def outline(c,x,y,w,h,color):
    rect(c,x,y,w,1,color);rect(c,x,y+h-1,w,1,color)
    rect(c,x,y,1,h,color);rect(c,x+w-1,y,1,h,color)


def pane(c,x,y,w,h,title,color=JADE):
    rect(c,x,y,w,h,mix(DEEP,color,.055))
    outline(c,x,y,w,h,mix(BG,color,.38))
    label(c,title,x+5,y+9,5,mix(BG,color,.75))
    rect(c,x+2,y+12,w-4,1,mix(BG,color,.22))


def lines(c,rows,x,y,size=6,step=11,dim=.65):
    for i,row in enumerate(rows):
        value,color=row if isinstance(row,tuple) else (row,TEXT)
        label(c,value,x,y+i*step,size,mix(BG,color,dim))


def heading(c,rank,rows,y=33):
    width=ROOMS[rank].rect[2]
    size=min(12,(width-28)/max(len(row) for row in rows)/.6)
    for i,row in enumerate(rows):label(c,row,14,y+i*(size+3),size,ACCENTS[rank//3])


def wire(c,a,b,color=JADE,thickness=2):
    c.set_source_rgb(*color);c.set_line_width(thickness)
    c.move_to(*a)
    c.curve_to(a[0],a[1]+45,b[0],b[1]+32,*b);c.stroke()


def plug(c,x,y,color=MUTED):
    rect(c,x-4,y-6,8,10,color)
    rect(c,x-3,y-10,6,5,mix(TEXT,DEEP,.3))
    rect(c,x-2,y-8,1,2,DEEP);rect(c,x+1,y-8,1,2,DEEP)


def check(c,x,y,color=GREEN):
    rect(c,x,y+3,2,2,color);rect(c,x+2,y+5,2,2,color)
    for i in range(4):rect(c,x+4+i,y+4-i,2,2,color)


def background(c,rank):
    w,h=ROOMS[rank].rect[2:]
    accent=ACCENTS[rank//3]
    stage_scenes.foundation(c,rank)
    # Sparse circuit traces give the dark desktop physical texture.
    for i in range(8 if rank//3 in (0,4) else 0):
        x=9+(i*41+rank*17)%(w-18)
        y=20+(i*37+rank*29)%(h-35)
        color=mix(BG,accent,.075)
        rect(c,x,y,min(23,w-x-2),1,color)
        rect(c,x,y,1,17,color);rect(c,x-1,y+16,3,3,color)
    if rank==0:
        heading(c,rank,('MY CODE.','MY KEYBOARD.'))
        label(c,'// no assistant needed',15,63,6,MUTED)
        pane(c,12,103,215,120,'nvim  ~/code/main.py')
        lines(c,[('01  def build_it():',CYAN),'02      read_the_docs()',
                 '03      think()',('04      write_the_code()',TEXT),
                 '05      make_it_work()',('06  # all me.',JADE)],22,128,7,14)
        # Loose braided keyboard lead, tucked behind the giant solid keycaps.
        wire(c,(120,265),(269,187),mix(BG,MUTED,.65),3)
        plug(c,269,187,mix(BG,TEXT,.4))
    elif rank==1:
        heading(c,rank,('AI SETTINGS',))
        label(c,'integration',15,53,6,MUTED)
        outline(c,14,69,w-32,40,JADE)
        rect(c,18,73,28,32,PANEL)
        label(c,'OFF',54,95,17,TEXT)
        lines(c,[('completion  [ ]',JADE),'agents      [ ]','suggestions [ ]'],14,117,5.5,8,.9)
        lines(c,['# saved locally'],14,290,5.5,12)
        wire(c,(13,334),(60,413),MUTED,2);plug(c,60,413)
        label(c,'unplugged',20,433,7,MUTED)
    elif rank==2:
        heading(c,rank,('JUST AUTOCOMPLETE.',))
        label(c,'// nothing to see here',14,54,7,MUTED)
        # This screen sits exactly inside the physical monitor casing.
        rect(c,56,116,110,120,DEEP)
        lines(c,[('~ $ complete',CYAN),'def hello():','  print("hel")','',
                 ('# suggested:',MUTED),('  "hello"',JADE)],62,132,6,12,.85)
        wire(c,(79,260),(205,251),mix(BG,MUTED,.6),3)
        plug(c,205,251,mix(BG,TEXT,.6))
        label(c,'TAB',204,110,17,mix(BG,JADE,.3))
    elif rank==3:
        label(c,'FAILED',75,46,10,RED)
        lines(c,['expected: works','received: nope'],12,62,6,11,.7)
        lines(c,[('E042: again?',RED),'retry  retry  retry'],12,115,6,11,.7)
    elif rank==4:
        heading(c,rank,('CPU 100%',))
        label(c,'agent: fixing the fix...',16,91,7,RED)
        # A square PC fan housing, screws, grille and wires: computer hardware.
        rect(c,32,121,214,218,mix(DEEP,PANEL,.3))
        outline(c,32,121,214,218,mix(MUTED,RED,.3))
        for x in (39,237):
            for y in (128,330):
                rect(c,x-2,y-2,5,5,MUTED);rect(c,x-1,y,3,1,DEEP)
        for r in (65,80,96):
            c.set_source_rgb(*mix(BG,MUTED,.4));c.set_line_width(1)
            c.arc(139,232,r,0,math.tau);c.stroke()
        lines(c,['tasks: 12','fixed:  0'],35,311,6,11,.8)
        label(c,'fix_final_FINAL_v9',16,350,6,MUTED)
    elif rank==5:
        heading(c,rank,('git revert',))
        # A git graph replaces the hanging hammer and medieval chains.
        rect(c,22,65,2,348,mix(BG,RED,.45))
        for i,word in enumerate(('oops','fix','fix2','fix3','undo','undo2','revert')):
            y=80+i*49
            outline(c,18,y-4,10,10,mix(BG,RED,.7))
            label(c,word,34,y+4,6,mix(BG,RED,.8))
            if i%2:
                rect(c,24,y+8,26,1,mix(BG,PINK,.35))
                rect(c,49,y+8,1,19,mix(BG,PINK,.35))
        label(c,'- trust',35,418,8,RED)
    elif rank==6:
        heading(c,rank,('PERMISSION REQUIRED',))
        pane(c,67,46,151,84,'agent wants to edit app.py',YELLOW)
        lines(c,[('READ    yes',GREEN),('WRITE   ask',YELLOW),('RUN     ask',YELLOW)],79,73,8,15,.95)
        # A little pixel mouse pointer reinforces that these are actual dialog controls.
        for row,length in enumerate((1,2,3,4,5,6,7,4,2)):
            rect(c,196,85+row,length,1,TEXT)
        lines(c,['scope: this file','time: just once'],15,159,7,13,.7)
        label(c,'nothing without my say-so',15,291,7,MUTED)
    elif rank==7:
        heading(c,rank,('ONLY THE TESTS.',))
        label(c,'app.test  [+]',12,49,6,YELLOW)
        rect(c,22,77,1,161,mix(BG,YELLOW,.23))
        lines(c,[('1  test("works")',CYAN),'2    expect(ok)',('3    assert(pass)',GREEN),
                 '4','5  // just this.'],11,95,6,12,.75)
        lines(c,['write app.py?','[ denied ]'],16,192,7,15,.9)
    elif rank==8:
        heading(c,rank,('I REVIEW EVERY LINE.',))
        label(c,'999+ changes waiting',14,56,8,YELLOW)
        rect(c,w//2,70,1,h-82,mix(BG,MUTED,.45))
        label(c,'BEFORE',12,82,6,RED);label(c,'AGENT',153,82,6,GREEN)
    elif rank==9:
        heading(c,rank,('SESSION','EXPIRED.'),27)
        lines(c,['last active:','30 days ago'],13,91,6,10,.65)
        wire(c,(30,98),(36,191),mix(BG,BLUE,.4),4)
        plug(c,36,191,mix(BG,BLUE,.7))
        rect(c,26,204,20,13,mix(BG,MUTED,.4))
        outline(c,29,207,14,6,DEEP)
        label(c,'disconnected',12,233,6,MUTED)
    elif rank==10:
        heading(c,rank,('I USED TO KNOW THIS.',))
        label(c,'how do I...',60,90,10,MUTED)
        for a,b in (((220,265),(132,193)),((126,193),(23,94)),((25,94),(177,70))):
            wire(c,a,b,mix(BG,BLUE,.2),2)
        lines(c,['// remember this?', 'function ...', '    ...'],84,118,7,17,.24)
        plug(c,136,226,mix(BG,MUTED,.65))
        label(c,'no suggestions',14,266,6,MUTED)
    elif rank==11:
        label(c,'03:17',15,35,22,BLUE)
        pane(c,12,77,116,120,'nvim  untitled',BLUE)
        label(c,'1',17,107,7,MUTED)
        label(c,'-- INSERT --',17,187,5.5,mix(BG,BLUE,.45))
        # Light from the small desk lamp reaches across the empty editor.
        c.set_source_rgba(*YELLOW,.035)
        c.move_to(35,194);c.line_to(4,235);c.line_to(100,235);c.close_path();c.fill()
    elif rank==12:
        heading(c,rank,('PAIR SESSION',))
        label(c,'you set the direction',14,54,7,TEXT)
        pane(c,11,65,112,230,'YOU',CYAN)
        pane(c,155,65,129,230,'AGENT',GREEN)
        lines(c,[('> build a thing',CYAN),'  constraints:', '  keep it small',
                 '  make it clear','','> nice. ship it.'],19,92,6,15,.7)
        lines(c,[('> on it.',GREEN),'  reading...', '  testing...',
                 '  checking...', '',('  done.',GREEN)],164,92,6,15,.7)
        # The solid central trunk becomes a USB hub; visible cables carry data.
        wire(c,(33,293),(201,309),mix(BG,CYAN,.35),4)
    elif rank==13:
        heading(c,rank,('CHECKS PASS',))
        label(c,'8 / 8',15,100,24,GREEN)
        for i,word in enumerate(('lint','unit','integration','build')):
            y=164+i*14
            check(c,13,y-5,mix(BG,GREEN,.75))
            label(c,word,29,y+2,6,mix(BG,TEXT,.7))
        label(c,'ready to merge',14,261,6,CYAN)
    else:
        heading(c,rank,('ENJOY THE RIDE.',))
        pane(c,12,68,121,151,'YOU / direction',CYAN)
        pane(c,147,68,119,151,'AGENT / execution',GREEN)
        label(c,'what next?',20,143,8,CYAN)
        label(c,'ready when you are',156,143,7,GREEN)
    dressing(c,rank)
    stage_scenes.dressing(c,rank)


def behind(c,rank,t,events=()):
    w,h=ROOMS[rank].rect[2:]
    if rank in (0,2,11):
        x,y={0:(102,193),2:(96,192),11:(29,101)}[rank]
        if int(t*1.8)%2:rect(c,x,y,5,8,JADE if rank<3 else BLUE)
    elif rank==3:
        if int(t*2)%2:rect(c,130,28,3,3,RED)
    elif rank==4:
        x,y=139,232
        for i in range(7):
            a=t*.6+sum(event['spin'] for event in events)+i*math.tau/7
            c.set_source_rgb(*mix(DEEP,MUTED,.55))
            c.move_to(x+math.cos(a)*15,y+math.sin(a)*15)
            c.curve_to(x+math.cos(a-.2)*48,y+math.sin(a-.2)*48,
                       x+math.cos(a+.12)*84,y+math.sin(a+.12)*84,
                       x+math.cos(a+.3)*86,y+math.sin(a+.3)*86)
            c.line_to(x+math.cos(a+.7)*78,y+math.sin(a+.7)*78)
            c.line_to(x+math.cos(a+.8)*18,y+math.sin(a+.8)*18)
            c.close_path();c.fill()
            c.set_source_rgb(*mix(BG,MUTED,.7));c.set_line_width(1)
            c.move_to(x+math.cos(a)*25,y+math.sin(a)*25)
            c.line_to(x+math.cos(a+.32)*78,y+math.sin(a+.32)*78);c.stroke()
        rect(c,x-13,y-11,26,22,DEEP)
        label(c,'CPU',x-10,y+3,8,TEXT)
        for i in range(12):
            value=5+int((math.sin(t*3+i*.7)+1)*7)
            rect(c,15+i*5,75-value,3,value,mix(RED,BG,.3))
    elif rank==5:
        y=70+(t*24)%325
        rect(c,20,y,6,3,RED)
    elif rank==6:
        glow(c,190,79,25,YELLOW,.06+.03*math.sin(t*2))
    elif rank==7:
        if int(t)%3:check(c,99,132,GREEN)
    elif rank==8:
        y=96+(int(t*.7)%13)*13
        rect(c,3,y-5,3,8,YELLOW)
    elif rank==9:
        if int(t)%5==0:rect(c,36,211,2,1,BLUE)
    elif rank==10:
        if int(t)%2:rect(c,82,69,6,1,BLUE)
    elif rank==12:
        for i in range(5):
            y=165+(i*29+t*20)%133
            rect(c,130,y,2,3,CYAN)
        if int(t)%2:rect(c,222,162,4,7,GREEN)
    elif rank==13:
        glow(c,43,89,40,GREEN,.035+.025*math.sin(t))
    elif rank==14:
        if int(t)%2:rect(c,113,197,5,7,CYAN)
        for i in range(4):
            x=20+(t*18+i*65)%243
            rect(c,x,225,3,1,mix(BG,CYAN,.5))
    for event in events:
        if event['kind']=='wake' and event['active']:
            strength=math.sin(math.pi*event['age']/event['duration'])
            if rank==2:
                glow(c,111,174,62,CYAN,.15*strength)
                label(c,'> hello, dev',62,223,6,mix(BG,GREEN,strength))
            elif rank==9:
                glow(c,34,167,45,BLUE,.13*strength)
                rect(c,34,211,4,2,mix(BG,CYAN,strength))
    animate(c,rank,t,events)
    stage_scenes.animate(c,rank,t)


def front(c,rank,t):
    surface_lights(c,rank,t)
