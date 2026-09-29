"""Search alternative jumps, including catch floors and casing tops.

This complements routecheck: a playable itinerary alone cannot detect bypasses.
The graph samples launch positions (including overhangs), all 36 charges and all
three directions using the real collision model. Each edge has a jump witness.
It is an optimistic graph: moving between two launch positions on a platform
may itself require a jump. Graph paths are not claimed as continuous playthroughs.
"""
import argparse
from collections import deque
from concurrent.futures import ProcessPoolExecutor
import json
import math
from .model import King, Tower, ledges
from .course import START, SUMMIT
from .physics_profile import PROFILE


MAX_RISE = PROFILE.jump_y_max**2/(2*PROFILE.gravity)
# Departure surfaces, not runtime gates. Connected casing tops at the same
# height count as legitimate precision alternatives to the broad departure ledge.
DEPARTURES = {
    2: ('exit',), 3: ('lip',), 4: ('exit',), 5: ('exit','wall'),
    6: ('exit',), 7: ('exit',), 8: ('exit','cap','mullion'), 9: ('rim',),
    10: ('exit',), 11: ('exit',), 12: ('exit',), 13: ('exit',),
}


def within_jump_envelope(source, target, scale):
    """Conservative free-flight bound, allowing edge overhang at both ends.

    Geometry can only shorten/rebound the arc, never add upward energy or
    horizontal speed. For ascending targets the full-charge arc therefore
    bounds every charge and wall bank. Descents are left to simulation.
    One native pixel of extra allowance covers contact nudges/rounding.
    """
    rise=(source.y-target.y)/scale
    if rise<=0:return True
    rise=max(0,rise-1)
    if rise>MAX_RISE:return False
    flight=(PROFILE.jump_y_max+math.sqrt(PROFILE.jump_y_max**2-
                                         2*PROFILE.gravity*rise))/PROFILE.gravity
    gap=max(target.left-source.right,source.left-target.right,0)/scale
    gap=max(0,gap-PROFILE.body_width-1)
    return gap<=PROFILE.jump_x_max*flight


def handoff_violations(bounds=(0,0,1600,900),seed=42):
    """Prove no early window entry, even from unsampled launch positions."""
    tower=Tower(bounds,seed);platforms=ledges(tower.near(0));violations=[]
    for source in platforms.values():
        origin,name=source.key.split(':');origin=int(origin)
        for target in platforms.values():
            destination=int(target.key.split(':')[0])
            if destination<3 or destination<=origin:continue
            permitted=(destination==origin+1 and name in DEPARTURES.get(origin,()))
            if not permitted and within_jump_envelope(source,target,tower.scale):
                violations.append((source.key,target.key))
    return violations


def standing_positions(platform, platforms, king, spacing=4):
    """Sample every exposed part, including the legal edge overhang."""
    a, b = platform.left-king.half+.02, platform.right+king.half-.02
    count = math.ceil((b-a)/(spacing*king.scale))
    for i in range(count+1):
        x = a+(b-a)*i/count
        if any(x+king.half>p.left+.01 and x-king.half<p.right-.01
               and platform.y>p.y+.01
               and platform.y-king.body_height<p.y+p.depth-.01
               for p in platforms.values() if p.key!=platform.key):
            continue
        yield x


def scan_source(args):
    source, bounds, seed, spacing = args
    tower = Tower(bounds,seed)
    platforms = ledges(tower.near(0))
    p = platforms[source]
    scale = tower.scale
    # No collision can add upward energy. Retain tall walls that extend into
    # the reachable band, plus a full screen of downward recovery trajectories.
    active = {key:b for key,b in platforms.items()
              if b.y+b.depth>=p.y-(MAX_RISE+PROFILE.body_height+2)*scale
              and b.y<=p.y+360*scale}
    edges = {}
    template = King(*bounds[2:])
    for x in standing_positions(p,active,template,spacing):
        for direction in (-1,0,1):
            for frames in range(1,PROFILE.charge_frames+1):
                k = King(*bounds[2:]);k.land(p,x)
                k.press();k.charge=frames/PROFILE.charge_frames;k.release(direction)
                for _ in range(150):
                    k.step(PROFILE.tick,active,0,bounds)
                    if k.room is not None:
                        if k.room!=source and not k.falls and k.room not in edges:
                            edges[k.room] = dict(source=source,target=k.room,x=x,
                                                 frames=frames,direction=direction,
                                                 land_x=k.x)
                        break
                    if k.y>p.y+360*scale:
                        break
    return source,edges


def scan(bounds=(0,0,1600,900),seed=42,spacing=4,workers=4):
    platforms = ledges(Tower(bounds,seed).near(0))
    args = [(key,bounds,seed,spacing) for key in platforms]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return dict(pool.map(scan_source,args))


def shortest_path(graph,start=START,end=SUMMIT,exclude=()):
    queue = deque([(start,[start])]);seen={start}
    while queue:
        key,path=queue.popleft()
        if key==end:return path
        for target in graph.get(key,{}):
            if target not in seen and target not in exclude:
                seen.add(target);queue.append((target,path+[target]))
    return None


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--spacing',type=float,default=4)
    parser.add_argument('--width',type=int,default=1600)
    parser.add_argument('--height',type=int,default=900)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    graph=scan((0,0,args.width,args.height),args.seed,args.spacing)
    path=shortest_path(graph)
    violations=handoff_violations((0,0,args.width,args.height),args.seed)
    bypasses=[room for room in range(1,15) if shortest_path(
        graph,exclude=[key for key in graph if key.startswith(f'{room}:')])]
    with open(args.output,'w') as out:
        json.dump(dict(seed=args.seed,bounds=[0,0,args.width,args.height],
                       spacing=args.spacing,graph=graph,optimistic_path=path,
                       handoff_violations=violations,skippable_windows=bypasses),out,indent=2)
    print('Optimistic path (not a continuous replay):',path)
    print('Early handoffs within jump envelope:',violations)
    print('Skippable windows in sampled graph:',bypasses)
