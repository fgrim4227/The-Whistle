import math

import pygame

from src.states.entity.monster.MonsterBaseState import MonsterBaseState
from src.systems import Pathfinding

WAYPOINT_ARRIVAL_DIST = 10.0

# How far outside the hiding spot's own edge the approach point sits.
# The spot is solid ground now, so a point right on top of it could
# never actually be reached; standing this close still reads as
# "cornered at the wardrobe" once the reveal plays.
APPROACH_MARGIN = 28.0

# Longest the walk over to the hiding spot may take before the capture
# resolves anyway.
APPROACH_TIMEOUT = 6.0


class MonsterCatchingState(MonsterBaseState):
    """
    A scripted, inescapable capture: the player tried to hide somewhere
    El Silbón already suspected. It first walks a real route to a clear
    spot right next to the hiding place it was only close enough to
    suspect it, not standing right there and only once it actually
    arrives does it hold still through its one-shot "catching" animation.
    PlayState dims the room and waits for that animation to finish, then
    pushes the jumpscare.
    """

    def enter(self, spot=None, *args, **kwargs) -> None:
        self.spot = spot
        self.path = []
        self.path_index = 0
        self.path_computed = False
        self.approach_x = None
        self.approach_y = None
        self.approach_timer = APPROACH_TIMEOUT
        self.approaching = spot is not None
        if not self.approaching:
            self._start_reveal()

    def process_ai(self, house, player, dt: float) -> None:
        if not self.approaching:
            return

        # The player can't leave the hiding spot while this is playing out,
        # so the walk over is never allowed to last forever: if the way
        # there turns out to be blocked, the reveal happens regardless.
        self.approach_timer -= dt
        if self.approach_timer <= 0.0:
            self._start_reveal()
            return

        current_room = house.rooms.get(self.monster.current_room_name)
        if not current_room:
            self._start_reveal()
            return

        obstacles = current_room.get_obstacles()

        if not self.path_computed:
            self.approach_x, self.approach_y = self._pick_approach_point(current_room, obstacles)
            route_width, min_route_width = self.monster.get_route_widths()
            self.path = Pathfinding.find_path(
                current_room, self.monster.get_collision_center(), (self.approach_x, self.approach_y),
                entity_width=route_width, min_entity_width=min_route_width,
            )
            self.path_index = 0
            self.path_computed = True

        if not self.path:
            # No route was found to the approach point push straight
            # toward it instead of standing frozen in place, the same
            # fallback every other movement state already has for when
            # find_path() comes back empty.
            if self.monster.approach_directly(self.approach_x, self.approach_y, obstacles, dt, WAYPOINT_ARRIVAL_DIST):
                self._start_reveal()
            return

        if self.path_index < len(self.path):
            step_x, step_y = self.path[self.path_index]
            self.monster.move_towards(step_x, step_y, obstacles, dt)

            mx, my = self.monster.get_collision_center()
            if math.hypot(step_x - mx, step_y - my) < WAYPOINT_ARRIVAL_DIST:
                self.path_index += 1
        else:
            self._start_reveal()

    def _pick_approach_point(self, current_room, obstacles):
        """
        The point just outside the hiding spot, on whichever side is both
        clear and closest to where the monster already is checked
        against the monster's own collision size, so it's a point the
        monster can actually stand at rather than one merely outside the
        spot's rect. Tried in all 8 compass directions and at a couple of
        margins, since a spot pushed into a corner or against a wall can
        have most of those directions blocked or off the room entirely.
        """
        rect = self.spot.get_rect()
        collision_rect = self.monster.get_collision_rect()
        half_w, half_h = collision_rect.width / 2.0, collision_rect.height / 2.0
        probe = pygame.Rect(0, 0, collision_rect.width, collision_rect.height)

        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (-1, -1), (1, -1), (-1, 1), (1, 1),
        ]
        clear_candidates = []
        for dx, dy in directions:
            for margin in (APPROACH_MARGIN, APPROACH_MARGIN * 1.5, APPROACH_MARGIN * 2.0):
                cx = rect.centerx + dx * (rect.width / 2.0 + margin)
                cy = rect.centery + dy * (rect.height / 2.0 + margin)
                cx = max(half_w, min(current_room.width - half_w, cx))
                cy = max(half_h, min(current_room.height - half_h, cy))
                probe.center = (cx, cy)
                if not any(probe.colliderect(obs) for obs in obstacles):
                    clear_candidates.append((float(cx), float(cy)))
                    break

        if not clear_candidates:
            return float(rect.centerx), float(rect.centery)

        mx, my = self.monster.get_collision_center()
        return min(clear_candidates, key=lambda p: math.hypot(p[0] - mx, p[1] - my))

    def _start_reveal(self) -> None:
        self.approaching = False
        self.monster.vx = 0.0
        self.monster.vy = 0.0
        self.monster.is_moving = False
        self.monster.change_animation("catching")
        self.monster.current_animation.reset()
