# jump.exe: learning, commitment, and recovery

Fifteen individually authored windows form a fictional developer's five-year climb
from the black pill to the white pill. The world is an Omarchy-style desktop of
keycaps, terminals, PC cooling hardware, permissions, git diffs and disconnected
tools. The [story notes](STORY.md) describe the emotional arc and the
[style guide](STYLE.md) defines the visual language.

[View the complete course overview](course-overview.png). Its five columns show
stages separately for comparison; in the game they form one continuous vertical world.

## What the research says

These sources informed the redesign; the specific layouts and tuning below are ours.

- **Original developers:** In [Nexile's verified AMA](https://www.reddit.com/r/PS4/comments/hgb0nr/ama_we_are_nexile_games_and_ukiyo_publishing/),
  Theo Unland Karlsson explains that they eased the starting forest and extensively
  adjusted the other areas. The team also describes an unintended full-charge wall
  bounce found by speedrunners. The lesson is to tune learning and failure deliberately,
  and test alternative trajectories rather than assuming an intended path is exclusive.
- **Experienced map creators:** [The workshop's level-design guidance](https://teamnexile.github.io/jk-workshop-docs/level-making/tips/)
  is community advice hosted by Nexile, including tips from *Babe of Ascension* creator
  IntroCar. It discourages repeated tiny-platform jumps, isolated extreme jumps,
  abrupt difficulty spikes and ubiquitous enormous falls. Long falls belong in selected
  places; ordinary geometry should support varied challenges. It also recommends
  complete playthroughs and outside playtesters.
- **Firsthand design analysis:** [Johan Holm's analysis](https://johanholmgamedesign.wordpress.com/2020/01/19/minimalism-in-games-and-jump-king/)
  distinguishes collision shape, timing tolerance and the amount of lost progress.
  Undercharging and overcharging can have different costs. Repetition lets players
  discover safer setups, while occasional exposed jumps retain their tension.
- **The supplied gameplay:** [Matt Birrell / DevilSquirrel's TAS](https://www.youtube.com/watch?v=LZlo6TzL7N4)
  shows forest masses, enclosed drain passages, projecting rooftops, broken bridges
  and isolated late-game footholds. The stream returned HTTP 403 here; visual inspection
  used its public storyboard previews, roughly 4.9 seconds apart. This was not a
  frame-by-frame motion study. A tool-assisted route is not a beginner difficulty target.

## Design rule: difficulty and fall cost are separate

A demanding jump can be taught above a floor before it appears beside a deep opening.
Conversely, an easy-looking transfer can create tension because the landing has no
floor beneath it. Each window in `course.py` names its lesson and its failure context.

| Stage | Learning sequence | Failure pattern |
| --- | --- | --- |
| Denial | Three forgiving jumps climb HOME, SPACE and a monitor in the same direction. Visit AI settings, return to the high code tab, then circle the terminal casing. | The keyboard chassis and settings window's low sill catch early mistakes. |
| Anger | Cross build errors; enter the hot PC fan basin and circle its heat sinks; use the git deletion panel for rebounds. | The error window is exposed. The fan housing and git footer have local catch floors. |
| Bargaining | Jump around a permission dialog, climb test-file tabs and pass around the review pane's diff hunks. | The test file has no enclosing floor; the dialog base and review footer give relief. |
| Depression | Climb a depleted battery, cross two disconnected keys to the left and reverse across a void; reach the blank editor at 3 a.m. | Selected misses pass through earlier windows. The desk restores a broad recovery floor. |
| Acceptance | Cross the USB hub and passing CI jobs, then face the summit's narrow keys, capped wall bank, reversal and final gap to ENTER. | The motherboard and recovery connector catch selected long falls. The hardest room comes last, with local bank retries and exposed upper transfers. |

## The windows are part of the terrain

The world is authored in a 480-unit-wide coordinate system. Window footprints vary
from a short bridge to a tall shaft and a broad basin. Some transfers travel sideways;
others approach a vertically offset window. There is no universal three-platform
room and no automatic alternation/mirroring function. The route explicitly revisits
the first windows: **keyboard → settings → code tab → settings → terminal → settings → terminal casing**.
A window remains part of the route after you have left it.

Physical hardware and software surfaces have different silhouettes and textures:
raised keycaps, slotted PC cases, copper heat sinks, USB hubs, error notifications,
permission buttons, code tabs, diff hunks and desk wood. Background interface lines
are dim and thin. Solid controls have opaque bodies, bright top edges and bevels.
The fan blades, cursor, CPU graph, git activity and packets animate behind the fixed
collision surfaces. All fifteen scenes are drawn for their own window dimensions,
rather than stretching a common illustrated backdrop.
The character collides with the actual foreground masses, including undersides and
walls. Rendering and physics share the same rectangles. Covered top edges are hidden
so adjoining pieces read as connected terrain. Frames remain open/decorative.
Seed variation only shifts pane placements within small bounds; it preserves the
lessons and fall corridors. The artwork stays inside windows, and wallpaper is unchanged.

The camera follows both directions without screen teleports. Earlier panes remain
physical throughout a long fall. Twelve native windows are reused as necessary.
Falling below the entire tower returns to the starting basin; there are no intermediate
respawn checkpoints. A catch surface protects a trajectory, not all future progress.

## Validation and concrete fall examples

`routecheck.py` plans and replays a continuous **59-jump** itinerary. Each jump begins
where the previous one actually landed. Ground movement obeys wall collisions;
charging and release use real simulation ticks. The check rejects standing inside
terrain. It does not move the character directly to a convenient launch point.

The first seven jumps each have at least five consecutive successful charge values
on the seed-42 reference route. A mistiming audit perturbs each selected charge by
±2, ±4 and ±8 ticks, clamped to the supported range. On the 1600×900, seed-42 course:

- 209 tested attempts miss the intended landing.
- 155 of those are caught in the same window.
- Seventeen lose at least two native screen heights (720 world units).
- The largest tested setback from either of the first two windows is 104 world units.
- An undercharged first crossing and a rebound off its entry both land on the
  settings window's lower sill; a jump back to the keyboard rejoins the route.
- Later misses can pass through multiple earlier windows. These are collision
  outcomes from the actual geometry, not scripted catches or progress checkpoints.

The [recording-driven refactor](PLAYTEST.md) also checks routes that bypass the
walkthrough. A conservative jump envelope rejects early entries into every window
from BUILD FAILED onward; a separate sampled graph searches casing tops, catch
floors, overhangs and rebounds. The [continuous replay](course-playthrough.mp4)
shows the earlier layout with normal physics. The [summit replay](summit-gauntlet.mp4)
shows the new final challenge; its measured timing and recovery checks are in the
[summit follow-up](PLAYTEST.md#follow-up-the-summit-must-be-the-hardest-room).

These are results for a particular route and perturbation set, not player failure
rates or proof that the course is fun. Unit checks also replay the entire itinerary
across three seeds and landscape/portrait displays, check recovery from long-fall
landing surfaces, and verify window clipping and non-overlap. Human attempts still
matter for judging readability, pacing and frustration.

The battery-to-SLEEP jump in room 10 was revised after player feedback. The old
route required an awkward rebound with only two successful charge values on the
wide-screen reference route. That earlier fix extended the pane 20 native pixels
left, moved SLEEP 16 pixels down and narrowed it to 60 pixels, keeping the battery
and entry in place. The later layout refactor raises the whole window while
preserving that internal jump. A direct left jump from the battery's center has at
least five consecutive successful charge values across 480×360, 1600×900,
1920×1080 and 900×1600 displays, on seeds 0, 1 and 42. The continuous 57-jump route
still passes. [Physics replay](sleep-jump-proof.mp4) ·
[Trajectory review](sleep-jump-proof.png).

The right-to-left shelf jump in room 12 had a similar readability failure: the
98-pixel upper shelf overlapped the lower shelf and blocked normal left launches.
The route solver accepted a launch with the character's center beyond the lower
shelf's visible end, or a screen-edge rebound on narrow displays. The upper shelf
is now 54 pixels wide and 12 pixels lower, leaving a visible gap. Regression checks
use real charge/release input from four fully supported standing positions,
requiring at least five consecutive successful charge timings without a wall or
ceiling collision. They cover five display shapes (including 2048×1152 logical
pixels) and three seeds. The editor content moves down to clear the revised shelf.
[Physics replay](desk-jump-proof.mp4) · [Trajectory review](desk-jump-proof.png).

```sh
PYTHONPATH=src python -m jump_exe.routecheck --seed 42 --audit --output /tmp/course-report.json
PYTHONPATH=src python -m jump_exe.render_course
```

## Movement fidelity and art

[Retsu's firsthand guide](https://note.com/retsu_teno/n/n4b3c3ec029da) documents walking,
36 charge increments at 60 Hz, direction selected at release, advance jump input,
no charge meter and no airborne steering. Those behaviors are implemented. Held
Space buffers charging after landing/recovery; it does not automatically release a jump.

[Nexile's player-behaviour documentation](https://teamnexile.github.io/jk-workshop-docs/mod-making/player-behaviour/)
explains the state/collision structure but does not establish exact numerical physics
constants. `physics_profile.py` therefore keeps gravity, launch velocities, collider
size, restitution and heavy-landing recovery together as explicit tuning estimates.
Exact numerical parity with the original game remains unverified.

The eight-pose developer and four-pose caretaker are sampled from an original
generated transparent atlas. The player is roughly 30 logical pixels tall, with a
keyboard satchel, jade hoodie and cream beanie. Both axes scale uniformly
with the 480×360 reference canvas. This is not a recovered original hitbox.
[Artwork provenance and prompts](../assets/PROVENANCE.md) document the generated assets.
No original game sprites, maps or video frames are shipped.
