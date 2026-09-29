"""Reference-scale tuning. See DESIGN.md for verified rules vs tuned constants."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicsProfile:
    tick: float = 1/60
    charge_frames: int = 36
    reference_width: int = 480
    reference_height: int = 360
    body_width: float = 18
    body_height: float = 28
    sprite_height: float = 30
    gravity: float = 1080
    walk_speed: float = 120
    jump_x_min: float = 54
    jump_x_max: float = 216
    jump_y_min: float = 162
    jump_y_max: float = 600
    terminal_speed: float = 900
    wall_restitution: float = .5
    head_restitution: float = .15
    heavy_landing_speed: float = 620
    heavy_landing_seconds: float = .32

    def scale(self, width, height):
        return min(width/self.reference_width,height/self.reference_height)


PROFILE = PhysicsProfile()
