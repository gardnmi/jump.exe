"""A mountain of oversized desktop objects, with routes that revisit windows."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Block:
    name: str
    x: int
    y: int
    w: int
    h: int
    material: str = 'board'


@dataclass(frozen=True)
class Room:
    title: str
    rect: tuple
    blocks: tuple
    route: tuple
    lesson: str
    fall: str
    landmark: str


def b(name,x,y,w,h,material='board'):
    return Block(name,x,y,w,h,material)


# Handoffs are authored against the *lowest* catch in the next window, not just
# its named entry. Otherwise recovery floors become elevators around the climb.
# The jump envelope and alternative-route scan live in shortcutcheck.py.
ROOMS = (
    Room('MY CODE, MY KEYBOARD',(20,0,300,300),(
        b('floor',0,278,300,22), b('home',96,244,60,34,'key'),
        b('spacebar',174,208,70,18,'key'), b('monitor',254,164,46,114,'crt'),
        b('loft',120,74,120,18,'tab'),
    ),('floor','home','spacebar','monitor','loft'),
         'Three forgiving jumps move in one direction. Leave the window, then return to its high editor tab.',
         'The first keys rise above a broad keyboard chassis. Missing the return jump lands on an earlier key.', 'keyboard'),
    Room('AI: DISABLED',(334,-240,136,480),(
        b('floor',0,454,136,26,'crt'), b('entry',20,354,88,26,'crt'),
        b('middle',20,240,98,16,'toggle'), b('upper',50,136,86,18,'toggle'),
        b('door',118,92,18,292,'crt'),
    ),('entry','middle','upper'),
         'The middle toggle meets the right case wall, making the return to the code tab useful. Circle the terminal instead of climbing a spare settings roof.',
         'Its low hardware sill catches undercharged first crossings; a jump back to the keyboard recovers the route.', 'settings'),
    Room('JUST AUTOCOMPLETE',(26,-355,290,300),(
        b('entry',215,280,75,20,'key'), b('chin',170,188,120,18,'crt'),
        b('base',40,236,142,24,'crt'), b('bezel',40,116,16,120,'crt'),
        b('side',166,112,16,52,'crt'), b('crown',40,92,142,24,'crt'),
        b('exit',195,30,95,16,'panel'),
    ),('entry','chin','crown','exit'),
         'Circle one giant monitor: its bezel is a wall, its casing a landing, its crown a launch point.',
         'The casing catches undershoots. The open side returns to the settings window instead of a reset.', 'terminal'),
    Room('BUILD FAILED',(330,-580,142,160),(
        b('entry',0,136,52,24,'error'), b('shard',75,79,43,17,'error'),
        b('lip',0,20,64,18,'error'),
    ),('entry','shard','lip'),
         'Cross three red build-error panels. The short window has no enclosing floor.',
         'The first genuinely exposed misses fall toward the earlier terminal and settings window.', 'errors'),
    Room('FAN AT 100%',(20,-1036,275,380),(
        b('floor',0,356,275,24,'case'), b('entry',200,300,75,18,'case'),
        b('tooth',0,268,74,22,'heatsink'), b('valve',92,188,76,24,'heatsink'),
        b('rim',214,126,61,24,'heatsink'), b('exit',80,50,96,26,'case'),
        b('jaw',0,104,24,164,'heatsink'),
    ),('floor','tooth','valve','rim','exit'),
         'Clear the last build error to enter the cooling basin. Circle RAM, CPU and VRAM to reach RETRY; the GPU is a recovery shelf.',
         'A deep local catch contains the first attempts; the outgoing transfer is a long commitment.', 'fan'),
    Room('REVERT EVERYTHING',(340,-1536,130,455),(
        b('floor',0,430,130,25,'diff'), b('entry',0,306,60,18,'diff'),
        b('flange',72,226,58,18,'diff'), b('release',0,134,52,20,'diff'),
        b('wall',100,40,30,390,'diff'), b('exit',90,38,40,20,'diff'),
    ),('floor','entry','flange','release','exit'),
         'Enter the git footer from RETRY. Bank around the first hunk, then alternate sides. Launch from the left third of UNDO through the recessed REVERT overhang.',
         'The terminal footer catches inward misses; the exposed left edge can undo the climb through the overheated PC.', 'git'),
    Room('ASK EVERY TIME',(20,-1898,280,340),(
        b('floor',0,318,280,22,'case'), b('entry',190,216,90,14,'toggle'),
        b('pan',0,256,94,14,'toggle'), b('stem',133,146,14,172,'case'),
        b('beam',74,126,138,18,'toggle'), b('exit',218,62,62,18,'file'),
    ),('floor','entry','beam','exit'),
         'Launch from ALLOW ONCE around the dialog overhang, then climb its ASK EVERY TIME control.',
         'The DENY button and monitor base catch misses before the exposed test-file climb.', 'permissions'),
    Room('JUST THE TESTS',(335,-2196,140,290),(
        b('entry',0,250,85,16,'file'), b('fold',90,160,50,14,'file'),
        b('crease',130,174,10,116,'file'), b('exit',0,62,46,14,'file'),
    ),('entry','fold','exit'),
         'Launch from the left quarter of UNIT TESTS to the recessed INTEGRATION tab, then reverse left from its middle to ONLY TESTS. Both tall jumps require measured charges.',
         'There is no broad floor. The permissions window below provides the nearest refuge.', 'tests'),
    Room('I REVIEW EVERYTHING',(15,-2528,280,320),(
        b('floor',0,296,280,24,'diff'), b('entry',204,276,76,20,'diff'),
        b('latch',104,206,66,16,'diff'), b('cap',176,22,16,184,'diff'),
        b('arch',0,116,66,20,'diff'), b('hinge',94,60,74,18,'diff'),
        b('exit',204,22,76,20,'diff'), b('mullion',264,42,16,104,'diff'),
    ),('floor','latch','arch','hinge','exit'),
         'The tall diff divider closes the right-side ladder. Cross to the deleted hunk, climb CHANGE, then clear the divider to APPROVE.',
         'The lower sill catches local mistakes. The outer transfer leaves that protection.', 'review'),
    Room('SESSION EXPIRED',(330,-2894,142,280),(
        b('entry',20,250,88,14,'panel'), b('bell',98,142,44,138,'battery'),
        b('rim',0,64,60,18,'crt'),
    ),('entry','bell','rim'),
         'Climb the empty battery, then use a direct left jump to the offset sleeping monitor rim. The approach clears its underside.',
         'Misses leave the window through the open chassis and can fall through several years.', 'idle'),
    Room('I USED TO KNOW THIS',(60,-3176,260,285),(
        b('entry',186,246,74,20,'key'), b('control',100,169,58,24,'key'),
        b('undo',0,68,48,26,'key'), b('exit',148,40,58,26,'key'),
    ),('entry','control','undo','exit'),
         'Two leftward jumps across lost keys followed by one deliberate reversal across a large empty gap.',
         'The open void is an intentional long-fall corridor; other routes provide the relief.', 'lostkeys'),
    Room('CURSOR AT 3AM',(335,-3452,140,265),(
        b('floor',0,235,140,30,'desk'), b('entry',0,216,140,19,'desk'),
        b('shelf',82,128,58,16,'desk'), b('exit',0,58,54,16,'desk'),
    ),('entry','shelf','exit'),
         'A lit desk after the disconnected keys. Jump left from the middle of the right shelf through the clear gap to the shorter upper shelf.',
         'The whole bottom of the window is a refuge; errors inside remain close.', 'lamp'),
    Room('PAIR SESSION',(6,-3816,295,330),(
        b('floor',0,308,295,22,'board'), b('entry',200,276,95,20,'cable'),
        b('trunk',124,160,26,148,'cable'), b('arm',148,242,56,14,'cable'),
        b('neck',124,138,26,22,'cable'), b('joint',150,228,12,14,'cable'),
        b('fork',162,220,90,16,'cable'), b('branch',26,122,124,16,'cable'),
        b('exit',204,48,91,18,'cable'),
    ),('entry','fork','branch','exit'),
         'Climb a shared workstation: cross the USB hub, circle its connectors, then reach the connected terminal.',
         'The motherboard forms a basin. Earlier precision gives way to generous cable connections.', 'pair'),
    Room('TESTS GREEN',(335,-4110,140,270),(
        b('entry',0,234,95,18,'panel'), b('bridge',55,138,85,14,'panel'),
        b('exit',0,44,95,18,'panel'), b('rail',132,44,8,94,'case'),
    ),('entry','bridge','exit'),
         'Climb green CI jobs, then bank off the visible right-hand status rail to reach MERGE.',
         'The outer edge remains exposed; the shared workstation below catches inward mistakes.', 'ci'),
    Room('ENJOY THE RIDE',(20,-4480,295,330),(
        b('entry',196,288,99,24,'key'), b('landing',10,218,106,24,'key'),
        b('bridge',86,112,135,18,'panel'), b('summit',180,38,115,22,'key'),
        b('tower',272,60,23,160,'case'), b('foot',272,312,23,18,'case'),
    ),('entry','landing','bridge','summit'),
         'Cross left from SPACE to SHIFT, make the tall jump to CHECKS PASS, then reverse toward ENTER and the white pill.',
         'The climb ends on a broad ENTER key, but falling remains physical.', 'desktop'),
)

START = '0:floor'
SUMMIT = '14:summit'
SPAWN_FRACTION = 1/6
GUIDE_POINT = (0,24,278)
BLACK_PILL = (0,79,263)
WHITE_PILL = (14,236,38)
# The opening explicitly revisits windows; window number is not progression order.
ROUTE = (
    '0:floor','0:home','0:spacebar','0:monitor','1:entry','0:loft','1:middle',
    '2:entry','1:upper','2:chin','2:crown','2:exit',
) + tuple(f'{i}:{key}' for i,room in enumerate(ROOMS) if i>=3 for key in room.route)
