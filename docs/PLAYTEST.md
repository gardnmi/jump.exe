# Layout refactor after the September 28 recording

[Continuous normal-physics playthrough](course-playthrough.mp4) ·
[Updated layout](course-overview.png)

The problem was bypassing the challenges. Difficult retries in the recording were
not a reason to reduce jump difficulty. Movement, charge timing, character size,
collision response, camera behavior and fall penalties are unchanged.

## What the recording exposed

In an early playtest recording, around **1:13**, ACCEPT? leads directly
into the fan basin, without climbing BUILD FAILED. Around **1:24–1:25**, the route
from CPU through VRAM reaches the git window before RETRY. The later git-to-permissions
transfer also makes the upper part of the git climb unnecessary.

The old checker could complete a prescribed 55-jump itinerary, but did not ask
whether someone could go around it. Searching alternatives exposed further bypasses:
git directly to the test-file window, APPROVE directly to SLEEP, and the right side
of the paired workstation directly to CONNECTED. These later findings are simulation
results, not claims about what the player did in the recording. Dev flight near the
end of the recording is excluded from the gameplay findings.

## Geometry with a purpose

The [reference-video storyboards](https://www.youtube.com/watch?v=LZlo6TzL7N4)
show enclosed drain passages, projecting ledges and open gaps that connect falls
across screens. The available previews are sampled stills, not a complete motion
study. The useful pattern is that surrounding masses constrain an arc and give its
misses different consequences. [Nexile's hosted mapping advice](https://teamnexile.github.io/jk-workshop-docs/level-making/tips/)
also emphasizes distinct layouts and selected long falls. The following shapes are
original to this course.

| Area | Required engagement and allowed alternatives |
| --- | --- |
| Denial | The settings toggle meets the case wall, encouraging the return to the high code tab. Removing the spare settings roof closes the ladder around the terminal crown. The introductory keycaps still allow faster skilled jumps. |
| Build errors / fan | E:TYPE is the departure for the fan basin. The lower GPU is a catch, rather than a ladder straight to VRAM. RAM/CPU/VRAM offer one circuit; the narrow left heat-sink crown offers a full-charge alternative. RETRY is the departure for git. |
| Git | Enter through the footer and bank around the first deletion hunk. Its narrower top gives the bank physical clearance. The upper REVERT region is needed before crossing to permissions. |
| Permissions / tests | ALLOW ONCE and DENY offer right- and left-side recovery routes around the solid dialog stem. Both feed ASK EVERY TIME, then THIS FILE. The following test tabs remain exposed. |
| Review | A tall solid diff divider replaces the right-hand stepping stone. Climb REVIEW, cross left to the deleted hunk, then clear the divider. Landing on its narrow crown is a legitimate precision alternative to the CHANGE/APPROVE setup. |
| Depression | APPROVE can no longer skip the battery to SLEEP. ESC cannot jump straight to Z: CTRL sets up the taller left jump, followed by the reversal toward `?`. The desk retains its local catch. |
| Acceptance | The lower AGENT connector can no longer jump directly to CONNECTED: cross through the YOU side of the hub. A strong entry-to-YOU jump remains possible. The CI status rail provides a visible bank. The summit gauntlet now requires SPACE → SHIFT → RUN → CHECKS PASS → CTRL → ENTER. |

Window placement is measured against **every solid surface**, including the lowest
catch floor and small connector stubs. Some representative changes, in native units:

| Old bypass | Old vertical rise | Revised vertical rise |
| --- | ---: | ---: |
| ACCEPT? → fan floor | 139 | 355 |
| VRAM → git footer | −24 (downward) | 196 |
| Git UNDO → permissions floor | 16 | 178 |
| APPROVE → SLEEP | 148 | 324 |
| AGENT connector → CONNECTED | 151 | 172 |
| SHIFT → ENTER | 120 | 180 |

The continuous free-flight upper bound is about 166.7 units; the actual discrete
jump is slightly lower. Walls reduce momentum. The new placement prevents these
departures through geometry; there are no visit locks or invisible barriers.
Catch floors remain physical on the way down. All artwork remains inside windows.

## Stage identity without the soundtrack

A second review identified that the previous build's music carried too much of the
stage distinction. Each group now changes its dominant material, lighting, large
background motifs and motion cadence. The [five-stage art comparison](stage-preview.png)
and [animated room review](world-review.mp4) use the actual game renderer.

Denial combines warm phosphor, a personal photo and worn equipment. Anger uses
oxidized hardware, broken-display lines, heat and a terminal shredder. Bargaining
uses ruled scope grids, a large etched lock and stamped review sheets. Depression
leaves dark blue glass and empty space around disconnected tools, with one pool of
warm desk light. Acceptance lights the boards and cables, shows paired previews
being built, and moves checks toward completion. These visual differences reinforce
the existing return trips, banks, constrained turns, exposed islands and connected
crossings. They add no forces, moving colliders or changes to jump timing.

## Validation

- **57-jump continuous itinerary:** walking, charging, collisions and each previous
  landing are replayed by `routecheck.py`. Tests cover three seeds on landscape and
  portrait displays. The 1280×720 review video is an additional continuous replay.
- **Analytic handoff check:** every surface from BUILD FAILED onward is beyond the
  full-charge reach of unfinished earlier challenges. The check includes legal body
  overhang and tests 50 seeds on five display configurations, including offset monitors.
- **Alternative-jump search:** `shortcutcheck.py` samples launch centers at no more
  than four native units apart, every charge and all three directions, retaining
  side collisions, ceilings, screen banks and recovery surfaces. Neither the
  landscape seed-42 nor portrait seed-1 graph has a path that omits an entire window.
  Its graph is optimistic about walking between positions on a surface; its paths
  are not claimed as continuous player runs. Sampling is not a proof against every
  possible local shortcut; the separate analytic handoff bound covers between-sample
  positions for the later window departures.
- **Fall audit:** on the seed-42 reference route, 196 perturbed attempts miss their
  intended target; 146 land in the same window and 11 lose at least two native
  screen heights. One missed CTRL jump lands on the fan's left casing roughly
  2,000 units below. The first two windows' maximum sampled setback remains 104.
  A left-side permissions catch is replayed through DENY back to ASK EVERY TIME.
- **91 game tests pass**, including pixel-grid consistency, clipping through the
  full tower, story/encounters, dev mode, audio, collisions and shortcut regressions.

These checks establish playable routes and constrain bypasses; timing and enjoyment
still need human attempts on the revised layout.

## Follow-up: UNDO → REVERT

In a later playtest recording, repeated attempts around 6–8 seconds
hit the side of REVERT during the ascent. Simulation confirmed that the old
overhang blocked direct rightward jumps from fully supported UNDO positions.
The previous solver witness used a launch beyond UNDO's left edge and only a
two-tick charge window; merely completing the itinerary missed this design flaw.

REVERT now starts at local x=90 instead of 48, narrowing its top to 40 native
pixels. Its 96-pixel rise, the source ledge, wall, room placement and movement
physics are unchanged. The exposed rising arc makes the setup readable; the
smaller landing still requires a measured charge and retains overcharge falls.
UNDO remains too low to bypass REVERT and enter the permissions window.

A new regression uses actual charge/release input from three fully supported
positions on UNDO's left portion, on four display shapes and three seeds. Each
must have at least three consecutive successful charges with no side, ceiling
or monitor-edge rebound. Full charge must still fail. The
[short replay](revert-jump-proof.mp4) demonstrates a 26-tick right jump
from the left third; the [trajectory](revert-jump-proof.png) shows its clearance.

## Follow-up: UNIT TESTS → INTEGRATION → ONLY TESTS

The next screenshot exposed the same flaw in room 08. The 96-pixel INTEGRATION
tab started at x=44, intercepting rightward jumps from supported UNIT TESTS
positions. The subsequent left jump also needed a launch near or beyond the
far end of INTEGRATION to clear ONLY TESTS' overhang.

INTEGRATION is now 50 pixels wide at x=90; ONLY TESTS is 46 pixels wide at x=0.
Their 90- and 98-pixel rises are unchanged. The smaller tabs preserve measured
landings and the open fall corridor. UNIT TESTS still cannot reach ONLY TESTS
in one jump, and INTEGRATION still cannot bypass the exit into the next window.

The regression tests three fully supported launch positions for each jump,
all 36 charges, four display shapes and three seeds. Each setup needs at least
three consecutive successful charges without a head, side or screen rebound.
It also replays both jumps back-to-back with 26-tick charges, starting the second
from the first's actual landing with no repositioning. The
[first-jump replay](tests-jump-proof.mp4) and
[return trajectory](tests-exit-jump-proof.png) use the real renderer and physics.

## Follow-up: the summit must be the hardest room

The old final window offered three broad, open jumps. Its replacement is a
550-unit-tall hardware gauntlet, extending upward while preserving the incoming
SPACE key's world position. [Layout](summit-gauntlet.png) ·
[Normal-physics replay](summit-gauntlet.mp4).

SHIFT and RUN are 42 units wide; CTRL is 38. A long left crossing and a precise
return lead to RUN. The casing forces a rightward bank around CHECKS PASS, while
its underside rejects overcharging. From the supported right quarter of RUN,
30–32 charge ticks succeed across the four tested display shapes and three seeds;
full charge fails. Reverse toward CTRL, then commit across the last gap to ENTER.
The ENTER platform provides room for the earned ending animation.

The upper steps cannot be skipped by jumping from lower platforms, and the casing
tops are covered by ENTER. Sampled collision searches include edge overhang,
every charge, and all three release directions on landscape and portrait screens.
The continuous route now has **59 jumps**, replayed from each previous landing.

The reference mistiming audit includes local retries at RUN and upper misses that
fall about 890 units into the paired workstation. Its left basin now has a small
USB recovery connector; the YOU platform is recessed to clear that return arc.
This permits climbing out of the catch without a reset. The audit records 209
misses overall, 155 same-window catches, and 17 falls of at least two screens.
These are sampled outcomes, not player failure rates. All 102 game tests pass.

The artwork follows the longer climb, and the ending camera frames its upper
330 units. Celebration characters perch on the new real platforms, with the
Rust-to-assembly terminal fitted between CTRL and CHECKS PASS.

## Follow-up: the CI jump needs a real landing target

Player feedback identified a forced edge overhang on BUILD OK: reaching the wide
TESTS OK shelf required standing with the character's center at or beyond the
left edge of the launch platform.

TESTS is now a 36-unit platform at the far right, recessed 49 units from the old
shelf's left edge and raised 12 units. The vertical status rail is removed.
MERGE is recessed to 72 units wide, giving the return jump clear space while
preserving a supported launch into the final room.

The incoming jump works from the supported left side of BUILD OK; the return works from
the middle of TESTS. Both have at least three consecutive successful charge values
across four display shapes and seeds 0, 1, and 42. Tests require the entire physics
body to stand on the launch surface, a direct flight with no rebound, and a
supported departure from MERGE into the summit room. Full charge misses the two
internal targets; the smaller landing preserves the timing challenge. The middle
step cannot be skipped, and the full route still contains 59 jumps.

[BUILD OK → TESTS](ci-jump-proof.png) · [TESTS → MERGE](ci-exit-jump-proof.png).
The traces use normal charged jumps and the same renderer as the game.

## Summit finale

`render_ending.py` replays all 59 jumps and walks into the white pill using normal
physics before recording the ending. Its displayed statistics come from that
simulated climb. [Preview with sound](ending-preview.mp4).
Tests cover one-shot collection, frozen results, replay and restart, paused input
and focus loss, Enter repeat protection, native-pixel rendering, and muted audio.
The world pickup is tested at four animation times across all three Acceptance
windows. Camera framing is checked on four monitor shapes, including portrait.
The game was not launched into the user's workspace during this validation.

```sh
PYTHONPATH=src python -m jump_exe.routecheck --audit --output /tmp/course-route.json
PYTHONPATH=src python -m jump_exe.shortcutcheck --output /tmp/course-shortcuts.json
PYTHONPATH=src python -m jump_exe.render_playtest
python tools/test.py
```
