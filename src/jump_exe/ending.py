"""One-shot summit finale and immutable completion statistics; no GUI dependency."""

import math

RESULT_AT = 10.
PROJECT_PROMPT = "Let's port Rust to assembly."
AGENT_REPLY = 'Absolutely. How hard could it be?'


def in_world(ending):
    return bool(ending and ending.get('active') and ending.get('age',0)<RESULT_AT)


def focus_summit(camera,tower,dt):
    """Ease to the summit celebration; the tall approach remains below the frame."""
    _,y,_,height=tower.rectangle(14)
    height=min(height,330*tower.scale)
    top=camera.bounds[1]+max(28,(camera.bounds[3]-height)/2)
    target=min(0.,y-top)
    camera.offset+=(target-camera.offset)*(1-math.exp(-4*max(0,dt)))


def clock_text(seconds):
    minutes,seconds=divmod(int(max(0,seconds)),60)
    hours,minutes=divmod(minutes,60)
    return f'{hours}:{minutes:02}:{seconds:02}' if hours else f'{minutes}:{seconds:02}'


class Ending:
    def __init__(self):
        self.active=False
        self.age=0.
        self.stats=None
        self.hero_x=236.

    def begin(self,seconds,jumps,longest_fall,practice=False,hero_x=236.):
        if self.stats is not None:
            return False
        self.stats=dict(time=clock_text(seconds),jumps=jumps,
                        fall=f'{longest_fall/360:.1f}',practice=practice)
        self.active=True
        self.hero_x=hero_x
        return True

    def replay(self,hero_x=None):
        if self.stats is not None:
            self.active=True
            self.age=0.
            if hero_x is not None:self.hero_x=hero_x

    def update(self,dt):
        if self.active:self.age+=max(0,dt)

    def command(self,key):
        """Only an explicit fresh Enter advances; jump keys never skip the reward."""
        if not self.active:return None
        if key in ('return','kp_enter') and self.age>=1.:
            if self.age<RESULT_AT:
                self.age=RESULT_AT
                return 'skip'
            self.active=False
            return 'dismiss'
        if self.age>=RESULT_AT and key in ('r','n'):
            return 'restart' if key=='r' else 'new_seed'
        return None

    def state(self):
        return dict(active=self.active,age=self.age,hero_x=self.hero_x,
                    stats=dict(self.stats or {}))
