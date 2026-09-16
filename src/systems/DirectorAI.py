"""
The Director: the only component of El Silbón's AI that knows 
the player's actual location. It never directly controls the monster; 
that task falls to the reactive states defined in `src/states/entity/monster/`, 
which act solely based on what they have legitimately perceived. This is a 
reference to the AI in Alien Isolation
"""

import math
import random
from typing import Optional


# How long the monster has to have been wandering with nothing happening
# at all before the Director is willing to stir something up.
TENSION_THRESHOLD = 5.0

# How long it holds off entirely after a real chase, so a scare is
# followed by room to breathe instead of another scare.
COOLDOWN_AFTER_CHASE = 5.0

# A seeded noise lands somewhere in this band around the player: close
# enough to bring the monster into the area, never so exact that being
# found reads as the game looking at the player's coordinates.
NOISE_JITTER_MIN = 40.0
NOISE_JITTER_MAX = 100.0

# Radius handed to hear_noise. Generous on purpose -- the jitter above is
# what keeps the cue fair, so the cue itself may as well land.
NOISE_RADIUS = 300.0

# States where nothing is really going on, so pressure is free to build.
# "moving_to_door" belongs here: patrol hands off to it every few seconds
# just to wander, and treating that as activity would keep the pressure
# from ever building in the one case this exists for the player staying
# quiet in another room.
CALM_STATES = ("patrol", "moving_to_door")


class DirectorAI:
    def __init__(self) -> None:
        self.tension_timer = 0.0
        self.cooldown_timer = 0.0

    def update(self, monster, player, house, dt: float) -> None:
        if monster.ai_state == "chase":
            self.cooldown_timer = COOLDOWN_AFTER_CHASE
            self.tension_timer = 0.0
            return

        if self.cooldown_timer > 0.0:
            self.cooldown_timer -= dt
            return

        if monster.ai_state not in CALM_STATES:
            # Stalking, investigating, knocking: the monster's own senses
            # already have something to work with.
            self.tension_timer = 0.0
            return

        self.tension_timer += dt
        if self.tension_timer < TENSION_THRESHOLD:
            return

        if monster.ai_state != "patrol":
            # Mid-walk to a door. Hold the pressure and spend it once the
            # monster settles back into wandering, where a cue can land.
            return

        self.tension_timer = 0.0
        self._nudge(monster, player, house)

    def _nudge(self, monster, player, house) -> None:
        player_room = self._player_room(house)
        if player_room is None:
            return

        if monster.current_room_name != player_room:
            # Nothing from another room could plausibly be heard, so the
            # nudge is a preference about where to wander next instead.
            monster.director_room_hint = player_room
            return

        px, py = player.get_center()
        angle = random.uniform(0.0, math.tau)
        distance = random.uniform(NOISE_JITTER_MIN, NOISE_JITTER_MAX)
        monster.hear_noise(
            px + math.cos(angle) * distance,
            py + math.sin(angle) * distance,
            radius=NOISE_RADIUS,
        )

    @staticmethod
    def _player_room(house) -> Optional[str]:
        return house.current_room.name if house.current_room else None
