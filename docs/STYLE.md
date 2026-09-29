# Omarchy, at game scale

Reference: [Omarchy](https://omarchy.org/) and its published
[Osaka Jade theme](https://github.com/basecamp/omarchy/blob/master/themes/osaka-jade/colors.toml).
Local official Osaka Jade and Tokyo Night previews were also inspected. The game
freezes its own palette in `desktop_style.py`; it does not edit desktop settings.

## Common art rules

- Compose complete rooms at their authored native resolution. Scale the finished
  image once with nearest-neighbor filtering. Text, props, moving hardware, light
  and window borders must not be drawn at a different density afterward.
- The developer is roughly 30 native pixels tall. All twelve player/caretaker
  frames use one source scale and aligned feet, including crouches and impacts.
  Do not continuously stretch the character to fake breathing.
- Use the same jade, charcoal, cream and cyan family for characters, props,
  hardware and UI. Red signals frustration/errors, yellow permission/review,
  cool gray-blue inactivity and cyan/green collaboration. Stage color supplements
  recognizable situations; it does not carry the story alone.
- Hardware has dark outlines, a small set of shaded faces and a top-left highlight.
  Keycaps have a raised face and lower bevel; heat sinks have fins; PC cases have
  ports and vents; USB hubs have connectors. These silhouettes should read without
  tiny labels. Desk props receive the same treatment at their smaller scale.
- Software uses square borders, a consistent monospace face and restrained color.
  Background app content is dim and thin. Physical platforms have opaque bodies,
  visible depth, a bright top and a dark underside matching their exact collider.
- Keep devices literal. A cooling fan is a PC fan, a review is a git diff, and a
  connection is a USB cable. Do not replace them with ancient machinery, hanging
  scales, vines or monuments. Use existing app terminology and original writing.
- Small creatures use original native-pixel clusters in `critters.py`: ducks,
  bugs, penguins, a curled desk cat and a terminal helper share the outline,
  cream highlights and terminal accents.
  Encounters react to distance, landings or rebounds, then settle. They never
  change the solid geometry, shove the player or interrupt charged input.

Core colors: background `#111c18`, panel `#23372B`, jade `#509475`, text `#C1C497`,
highlight `#F6F5DD`, cyan `#2DD5B7`, error `#FF5345`, review `#E5C736`.
`SCENES` in `desktop_style.py` expands this family into five pane-local material
ramps: warm worn equipment, oxidized hot metal, amber documents, unlit blue glass,
and powered mint boards. Terrain uses those material ramps while retaining bright
collision tops and consistent bevels. Large shapes in `stage_scenes.py` distinguish
the rooms before a player reads any small text: fan housings, scope sheets, empty
switch beds and paired application previews. Static motifs are cached; moving
scanners, shredded changes, dust and build progress are drawn behind terrain.
The character adds a restrained skin-tone ramp. CaskaydiaMono Nerd Font is used
when installed, with Cairo's monospace fallback otherwise.

## Review at the size people play

`render_art_review.py` draws actual character frames, terrain and small props on
[one board](art-review.png). `render_story.py` and `render_course.py` render
the game's actual scene renderer, not an illustrative mockup. Inspect silhouettes,
caption clipping, contrast and apparent pixel size together, including tall panes.

`render_world.py` reviews all fifteen windows at an exact 2× scale. Its
[animation review](world-review.mp4) shows representative encounter states
alongside the ambient animations; it is not a gameplay recording. The separate
[SLEEP jump replay](sleep-jump-proof.mp4) runs actual charged-jump physics.

## Emotional cadence

- Denial is comfortable and defensive: warm desk objects, habitual saves and
  suggestions that appear, hesitate and get dismissed.
- Anger is restless: repeated printouts, discarded diffs, hot circuits and a
  busy fan. Motion comes from specific devices, without full-window flashes.
- Bargaining hesitates: permission cursors, individual review checks, locked
  source and a test meter that stalls.
- Depression slows down: sparse dust, sleeping hardware, erased questions and
  a cat on a neglected desk. Platform tops keep their readable contrast.
- Acceptance flows steadily: alternating terminal activity, connected packets,
  green checks, a responsive helper and gently moving leaves.

Books, notepads, printers and wastebaskets use the same bevels, palette and native
pixel grid as the existing props. Inset device LEDs stay below collision tops;
decorative circuits are thin and dim, while physical platforms retain solid depth.

`test_art.py` checks all fifteen rooms enlarged 3× exactly repeat their native
pixels, including text and active encounter effects, and that all sprite poses fit their
transparent canvases. These checks catch technical consistency failures; visual
judgment remains necessary for quality and readability.
