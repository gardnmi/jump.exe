# A living desktop

[Watch the five-stage preview](living-desktop.mp4) · [View the stills](living-desktop.png)

The windows and developer respond to proximity, jumps, and landings. These are
cosmetic reactions: charge timing, trajectories, collision, recovery, and every
platform remain the same.

| Stage | Environmental reactions | Character response |
| --- | --- | --- |
| Denial | Terminals wake, consider an assistant, then show `AI: disabled`. An autocomplete silhouette suggests a different jump; landings scatter discarded text. | Soft green screen light. |
| Anger | Vents blow paper, cable arcs spark, and hard impacts shake loose screws and casing dust. | The hood ruffles in nearby gusts; arcs briefly light the developer red. |
| Bargaining | A permission scanner follows the developer, then stamps `APPROVED`. Permission slips flutter and settle on hardware. | A narrow scan band outlines the sprite as it passes. |
| Depression | Landings lift heavy dust. Dark glass holds a delayed reflection; an approached cursor falls quiet, then slowly returns. | Weak, wavering blue screen light. |
| Acceptance | Landings send packets along circuit traces, complete little applications, and illuminate connected hardware. Checkmarks rise from the landing. | Cool terminal light swells as a build completes. |

Hard landings also settle the satchel, and debris inherits horizontal momentum.
Small moths shelter beside warm displays, startle when approached, and return.
Occasionally a nearby window wakes on its own. Effect cooldowns avoid constant
repetition; all motion stays inside game windows except the developer's own
lighting and clothing reactions.

## Rendering and validation

`atmosphere.py` observes the physics state without modifying it. Particles settle
on the existing terrain and expire; each room holds at most 48. The delayed
reflection uses a bounded pose history. Practice flight and the ending clear
transient effects, so teleporting cannot trigger a false hard landing.

`atmosphere_art.py` draws on the same native pixel grid as the room artwork.
Character reactions are composed into cached native sprite frames before scaling.
Glass effects sit behind terrain; surface debris is small and short-lived.

The tests compare a real charge/jump/landing simulation with and without the
observer, verify particle settling and reflection delay, check cleanup and
cooldowns, and compare native rendering with exact 3× pixel scaling in all rooms.

Regenerate the preview without opening desktop windows:

```sh
PYTHONPATH=src python -m jump_exe.render_atmosphere
```

The preview uses ordinary simulated physics and proximity events in five
representative rooms, including hard landings in Anger and Depression.
