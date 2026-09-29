"""A five-year story inside real windows; the desktop itself is never painted."""
from functools import lru_cache
import cairo
from .model import THEMES
from .course import ROOMS, SUMMIT
from .character import draw as draw_developer
from .environment import ambience, props
from .terrain import surfaces
from .landmarks import background, behind, front
from .desktop_style import BG,DEEP,PANEL,TEXT,WHITE,JADE,CYAN,MUTED,FONT,APPS,PATHS,SCENES,mix
from .story import YEARS
from .life import DesktopLife
from .critters import reactions
from .finale_art import draw_finale
from .ending import in_world
from .summit_animation import draw_world
from . import atmosphere_art

INK = TEXT
GOLD = (.96,.74,.35)


def box(c,x,y,w,h,color):
    c.set_source_rgb(*color)
    c.rectangle(round(x),round(y),round(w),round(h))
    c.fill()


def text(c,value,x,y,size=12,color=INK):
    c.set_source_rgb(*color)
    c.select_font_face(FONT,0,0)
    c.set_font_size(size)
    c.move_to(round(x),round(y))
    c.show_text(value)


def knight(c,x,y,facing,charge,phase=0,scale=2,pose='idle',effects=None):
    draw_developer(c,x,y,facing,scale,pose,phase,effects)


@lru_cache(maxsize=30)
def room_surface(rank, foreground=False):
    w,h=ROOMS[rank].rect[2:]
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    c=cairo.Context(surface)
    c.set_antialias(cairo.ANTIALIAS_NONE)
    if foreground:
        surfaces(c,rank)
    else:
        background(c,rank)
    return surface


def chrome(c,w,h,rank,t):
    _,bg,accent,_=THEMES[rank//3]
    # Square, restrained Omarchy borders and a terminal-style tab line.
    scene=SCENES[rank//3]
    edge=mix(accent,scene['metal'],.35)
    box(c,0,0,w,11,mix(DEEP,scene['back'],.45))
    box(c,0,0,w,1,edge);box(c,0,0,1,h,edge)
    box(c,w-1,0,1,h,edge);box(c,0,h-1,w,1,edge)
    box(c,3,3,5,5,accent)
    box(c,4,4,3,3,DEEP)
    text(c,APPS[rank],12,8,5,accent)
    if w>190:text(c,PATHS[rank],70,8,4.5,MUTED)
    text(c,f'{rank//3+1:02} / {rank+1:02}',w-34,8,4.5,TEXT)


@lru_cache(maxsize=15)
def frame_buffer(rank):
    return cairo.ImageSurface(cairo.FORMAT_ARGB32,*ROOMS[rank].rect[2:])


@lru_cache(maxsize=15)
def resting_encounters(rank):
    return DesktopLife().room(rank)


def tile(target,w,h,rank,level,t=0.,accepted=False,talking=False,events=None,ending=None,ambient=None):
    rw,rh=ROOMS[rank].rect[2:]
    # Compose everything at native resolution, including text, props and motion.
    # Upscale once so no effect or caption introduces a different pixel density.
    surface=frame_buffer(rank)
    c=cairo.Context(surface)
    c.set_antialias(cairo.ANTIALIAS_NONE)
    c.set_operator(cairo.OPERATOR_SOURCE)
    c.set_source_surface(room_surface(rank),0,0)
    c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint()
    c.set_operator(cairo.OPERATOR_OVER)
    c.save();c.rectangle(2,11,rw-4,rh-13);c.clip()
    ambience(c,rw,rh,rank,level,t)
    events=resting_encounters(rank) if events is None else events
    behind(c,rank,t,events)
    atmosphere_art.behind(c,rank,ambient)
    c.restore()
    c.set_source_surface(room_surface(rank,True),0,0)
    c.get_source().set_filter(cairo.FILTER_NEAREST);c.paint()
    props(c,rank,level,t,accepted,talking,celebrating=in_world(ending))
    front(c,rank,t)
    reactions(c,rank,events,t)
    c.save();c.rectangle(2,11,rw-4,rh-13);c.clip()
    atmosphere_art.front(c,rank,ambient)
    c.restore()
    chrome(c,rw,rh,rank,t)
    if in_world(ending):
        c.save();c.rectangle(1,1,rw-2,rh-2);c.clip()
        draw_world(c,rank,ending,room_surface(rank,True),room_surface(rank))
        c.restore()
    target.save()
    target.rectangle(0,0,w,h);target.clip()
    target.scale(w/rw,h/rh)
    target.set_source_surface(surface,0,0)
    target.get_source().set_filter(cairo.FILTER_NEAREST);target.paint()
    target.restore()


def wrapped(c,value,max_width,size):
    c.select_font_face(FONT,0,0)
    c.set_font_size(size)
    lines=[];line=''
    for word in value.split():
        candidate=(line+' '+word).strip()
        if line and c.text_extents(candidate).x_advance>max_width:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines


def hud(c,w,h,data):
    if data.get('ending',{}).get('active'):
        if in_world(data['ending']):
            hint='WHITE PILL FOUND  /  ENTER: RESULTS'
            if not data.get('focused',True):hint='PAUSED / click a platform window'
            c.set_source_rgba(*DEEP,.94);c.rectangle(16,h-44,min(w-32,380),28);c.fill()
            text(c,hint,28,h-25,11,CYAN)
        else:
            draw_finale(c,w,h,data)
        return
    level=data['level']
    name,bg,accent,_=THEMES[level]
    c.set_source_rgba(*bg,.92);c.rectangle(16,38,330,85);c.fill()
    box(c,16,38,3,85,accent)
    text(c,'JUMP.EXE / OMARCHY',30,60,15,INK)
    text(c,f'{YEARS[level]} / {name}',30,82,13,accent)
    text(c,f"{data['jumps']} jumps / {data['falls']} falls",30,104,11)
    hint='A/D WALK  |  HOLD + RELEASE SPACE: JUMP  |  F2 DEV  |  R RESTART  N NEW SEED  ESC EXIT'
    if data.get('practice_ready'):hint='A/D WALK  |  HOLD + RELEASE SPACE: JUMP  |  F2 FLY  F3 RETRY  |  R RESTART  ESC EXIT'
    if data.get('dev_mode'):hint='WASD / ARROWS: FLY  |  SHIFT FAST  CTRL SLOW  |  PGUP/DN ROOM  |  F2 PLAY  F3 RETRY  |  ESC EXIT'
    elif data.get('guide_near'):hint='E TALK  |  A/D WALK  |  HOLD + RELEASE SPACE: JUMP  |  F2 DEV  |  ESC EXIT'
    elif data.get('accepted') and data.get('platform')==SUMMIT:
        hint='E REPLAY ENDING  |  A/D WALK  |  SPACE JUMP  |  R CLIMB AGAIN  |  ESC EXIT'
    if data.get('music_available'):
        hint += f"  |  [ / ] MUSIC {data.get('music_volume',0)*100:.1f}%"
        hint += '  |  M '+('UNMUTE' if data.get('music_muted') else 'MUTE')
    if not data.get('focused'):hint='PAUSED / click any platform window to continue'
    lines=wrapped(c,hint,min(w-56,1110),11)
    height=14+len(lines)*17
    c.set_source_rgba(*bg,.94);c.rectangle(16,h-height-11,min(w-32,1140),height);c.fill()
    for i,line in enumerate(lines):text(c,line,28,h-height+7+i*17,11,accent)
    if data.get('dev_mode'):
        index=data.get('dev_room',0)
        blocked=data.get('dev_blocked')
        color=(1.,.42,.3) if blocked else GOLD
        c.set_source_rgba(.08,.07,.04,.95);c.rectangle(16,131,min(w-32,560),66);c.fill()
        box(c,16,131,3,66,color)
        text(c,f'DEV / {index+1:02} {ROOMS[index].title}',30,155,14,color)
        text(c,'INSIDE TERRAIN / move into open space to play' if blocked else
             'F2 resumes here and sets your F3 practice position',30,179,11,color)
    dialogue=data.get('dialogue',[])
    if dialogue:
        panel_w=min(450,w-40)
        lines=[line for sentence in dialogue for line in wrapped(c,sentence,panel_w-36,12)]
        panel_h=65+len(lines)*20
        x=max(20,min(w-panel_w-20,data.get('guide_x',data['x'])-data['origin'][0]-panel_w/2))
        y=max(140,min(h-panel_h-70,data.get('guide_y',data['y'])-data['origin'][1]-data['sprite_scale']*28-panel_h))
        c.set_source_rgba(.065,.077,.061,.96);c.rectangle(x,y,panel_w,panel_h);c.fill()
        box(c,x,y,2,panel_h,GOLD)
        text(c,'THE CARETAKER',x+18,y+25,11,GOLD)
        for i,line in enumerate(lines):text(c,line,x+18,y+49+i*20,12)
        text(c,f"E / {'CLOSE' if data.get('dialogue_page')==3 else 'CONTINUE'}",x+18,y+panel_h-12,10,accent)
    if data.get('accepted'):
        x=max(20,w/2-210)
        c.set_source_rgba(.09,.13,.08,.94);c.rectangle(x-15,38,435,50);c.fill()
        text(c,'WHITE PILL FOUND / ENJOY THE RIDE',x,68,16,(.96,.92,.7))
