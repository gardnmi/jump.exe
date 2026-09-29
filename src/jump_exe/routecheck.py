"""Play an authored itinerary using real walking, charged jumps and landings.

Unlike isolated reachability tests, each leg starts where the preceding jump
actually landed. Reports timing tolerance and can save a replay for inspection.
"""
import argparse
import copy
import json
import math
from .model import King, Tower, ledges
from .course import ROUTE, ROOMS
from .physics_profile import PROFILE


def rest(king,platforms,bounds):
    king.cancel()
    for _ in range(math.ceil(king.recovery/PROFILE.tick)+1):
        king.step(PROFILE.tick,platforms,0,bounds)


def walking_positions(king,platforms,bounds):
    yield copy.deepcopy(king),0,0
    for direction in (-1,1):
        k = copy.deepcopy(king)
        last = None
        for ticks in range(1,181):
            previous = copy.deepcopy(k)
            k.step(PROFILE.tick,platforms,direction,bounds)
            if k.room!=king.room:
                if last!=ticks-1:
                    yield previous,direction,ticks-1
                break
            if abs(k.x-previous.x)<.001:
                yield k,direction,ticks
                break
            if ticks%6==0:
                yield copy.deepcopy(k),direction,ticks
                last = ticks


def launch(standing,frames,direction,platforms,bounds,target_y):
    k = copy.deepcopy(standing)
    k.press()
    k.charge = frames/PROFILE.charge_frames
    k.release(direction)
    bounced = False
    for _ in range(120):
        vx = k.vx
        k.step(PROFILE.tick,platforms,0,bounds)
        bounced |= vx*k.vx<0
        if k.room is not None:
            return k,bounced
        if k.vy>0 and k.y>max(standing.y,target_y)+60*k.scale:
            break
    return k,bounced


def find_jump(king,target,platforms,bounds):
    rest(king,platforms,bounds)
    p = platforms[target]
    # Every collider that can affect an upward leg, including its approach.
    active = {key:block for key,block in platforms.items()
              if block.y+block.depth>=king.y-220*king.scale
              and block.y<=king.y+90*king.scale}
    rise = max(0,(king.y-p.y)/king.scale)
    velocity = math.sqrt(2*PROFILE.gravity*rise)
    first = max(1,math.floor(1+35*(velocity-PROFILE.jump_y_min)/
                              (PROFILE.jump_y_max-PROFILE.jump_y_min)))
    need = 5 if int(target.split(':')[0])<3 else 3
    best = None
    for standing,walk_direction,walk_ticks in walking_positions(king,active,bounds):
        toward = 1 if (p.left+p.right)/2>standing.x else -1
        for direction in (toward,0,-toward):
            group = []
            for frames in range(first,37):
                landed,bounced = launch(standing,frames,direction,active,bounds,p.y)
                if landed.room==target:
                    group.append((frames,landed,bounced))
                else:
                    group = []
                if group:
                    selected = group[len(group)//2]
                    witness = dict(source=king.room,target=target,walk_direction=walk_direction,
                                   walk_ticks=walk_ticks,charge_frames=selected[0],direction=direction,
                                   tolerance=len(group),full_charge=frames==36,
                                   bounced=selected[2],start_x=king.x,launch_x=standing.x,
                                   land_x=selected[1].x)
                    if best is None or len(group)>best[0]:
                        best = (len(group),selected[1],witness)
                    if len(group)>=need:
                        return selected[1],witness
    if best:
        return best[1],best[2]
    return None,None


def replay_step(king,witness,platforms,bounds):
    rest(king,platforms,bounds)
    for _ in range(witness['walk_ticks']):
        king.step(PROFILE.tick,platforms,witness['walk_direction'],bounds)
    king.press()
    for _ in range(witness['charge_frames']):
        king.step(PROFILE.tick,platforms,0,bounds)
    king.release(witness['direction'])
    for _ in range(180):
        king.step(PROFILE.tick,platforms,0,bounds)
        if king.room is not None:
            overlap = [p.key for p in platforms.values()
                       if king.x+king.half>p.left+.02 and king.x-king.half<p.right-.02
                       and king.y>p.y+.02 and king.y-king.body_height<p.y+p.depth-.02]
            if overlap:
                raise RuntimeError(f'Landing inside terrain: {overlap}')
            return


def solve(bounds=(0,0,1600,900),seed=42,verbose=False):
    tower = Tower(bounds,seed)
    platforms = ledges(tower.near(tower.base))
    king = King(*bounds[2:])
    king.enter(platforms)
    witnesses = []
    for target in ROUTE[1:]:
        landed,witness = find_jump(king,target,platforms,bounds)
        if landed is None:
            raise RuntimeError(f'Unreachable {king.room} -> {target}, x={king.x:.1f}')
        # Reproduce from the real preceding state using actual input ticks.
        replay_step(king,witness,platforms,bounds)
        if king.room!=target:
            raise RuntimeError(f'Replay landed on {king.room}, expected {target}')
        witnesses.append(witness)
        if verbose:
            print(f"{witness['source']} -> {target}: {witness['charge_frames']} frames, "
                  f"window {witness['tolerance']}, bank {witness['bounced']}",flush=True)
    return witnesses


def audit_falls(route,bounds=(0,0,1600,900),seed=42):
    tower = Tower(bounds,seed)
    platforms = ledges(tower.near(tower.base))
    king = King(*bounds[2:])
    king.enter(platforms)
    results = []
    for witness in route:
        rest(king,platforms,bounds)
        standing = copy.deepcopy(king)
        for _ in range(witness['walk_ticks']):
            standing.step(PROFILE.tick,platforms,witness['walk_direction'],bounds)
        frames_to_try = sorted({max(1,min(36,witness['charge_frames']+delta))
                                for delta in (-8,-4,-2,2,4,8)})
        for frames in frames_to_try:
            trial = copy.deepcopy(standing)
            trial.press()
            trial.charge = frames/36
            trial.release(witness['direction'])
            trace = [(trial.x,trial.y)]
            for tick in range(600):
                trial.step(PROFILE.tick,platforms,0,bounds)
                if tick%4==0:
                    trace.append((trial.x,trial.y))
                if trial.room is not None:
                    break
            if trial.room != witness['target']:
                results.append(dict(source=witness['source'],target=witness['target'],
                                    frames=frames,landed=trial.room,
                                    drop=round(max(0,(trial.y-standing.y)/king.scale),1),
                                    reset=trial.falls>standing.falls,land_x=trial.x,land_y=trial.y,trace=trace))
        replay_step(king,witness,platforms,bounds)
    return results


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--output')
    parser.add_argument('--audit',action='store_true')
    args = parser.parse_args()
    route = solve(seed=args.seed,verbose=True)
    falls = audit_falls(route,seed=args.seed) if args.audit else []
    if falls:
        long = [f for f in falls if f['drop']>=720]
        local = [f for f in falls if f['source'].split(':')[0]==f['landed'].split(':')[0]]
        print(f'Failed attempts: {len(falls)}; same-room catches: {len(local)}; 2-screen falls: {len(long)}')
        print('Opening worst drop:',max(f['drop'] for f in falls if int(f['source'].split(':')[0])<2))
    if args.output:
        with open(args.output,'w') as out:
            json.dump({'seed':args.seed,'bounds':[0,0,1600,900],'route':route,'falls':falls},out,indent=2)
    print(f'Complete: {len(route)} jumps with continuous walking and landings.')
