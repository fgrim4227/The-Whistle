import math

from src.states.entity.monster.MonsterBaseState import MonsterBaseState
from src.systems import Pathfinding

WAYPOINT_ARRIVAL_DIST = 10.0

# How close the monster has to be to the player before the reveal plays,
# measured between the two centers. Small enough that it reads as the
# monster standing right over them rather than grabbing from across the
# room; the monster doesn't collide with the player, so it can always
# close the last stretch.
CATCH_DISTANCE = 22.0

# Longest the walk over to the player may take before the capture
# resolves anyway.
APPROACH_TIMEOUT = 6.0


class MonsterCatchingState(MonsterBaseState):
    """
    A scripted, inescapable capture: the player tried to hide somewhere
    El Silbón already suspected. It walks a real route over to where the
    player actually is it was only close enough to suspect the spot,
    not standing on it and only once it's right on top of them does it
    hold still, turn to face them, and play its one-shot "catching"
    animation. PlayState dims the room and waits for that animation to
    finish, then pushes the jumpscare.
    """

    def enter(self, spot=None, *args, **kwargs) -> None:
        self.spot = spot
        self.path = []
        self.path_index = 0
        self.path_computed = False
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
            self._face(player)
            self._start_reveal()
            return

        current_room = house.rooms.get(self.monster.current_room_name)
        if not current_room:
            self._start_reveal()
            return

        obstacles = current_room.get_obstacles()
        px, py = player.get_center()
        mx, my = self.monster.get_collision_center()

        if math.hypot(px - mx, py - my) <= CATCH_DISTANCE:
            self._face(player)
            self._start_reveal()
            return

        # The player can't move while hidden, so the route there is worked
        # out once and then walked, not asked for again every frame.
        if not self.path_computed:
            route_width, min_route_width = self.monster.get_route_widths()
            self.path = Pathfinding.find_path(
                current_room, (mx, my), (px, py),
                entity_width=route_width, min_entity_width=min_route_width,
            )
            self.path_index = 0
            self.path_computed = True

        if self.path_index < len(self.path):
            step_x, step_y = self.path[self.path_index]
            self.monster.move_towards(step_x, step_y, obstacles, dt)

            mx, my = self.monster.get_collision_center()
            if math.hypot(step_x - mx, step_y - my) < WAYPOINT_ARRIVAL_DIST:
                self.path_index += 1
        else:
            # The route ends at the closest cell a body that wide can
            # stand on, which is still short of someone pressed up against
            # the furniture that last stretch gets closed head-on.
            self.monster.move_towards(px, py, obstacles, dt)

    def _face(self, player) -> None:
        """Turns to look at the player, so the reveal plays facing them."""
        px, py = player.get_center()
        mx, my = self.monster.get_collision_center()
        dx = px - mx
        dy = py - my
        if abs(dx) > abs(dy):
            self.monster.direction = "right" if dx > 0 else "left"
        else:
            self.monster.direction = "down" if dy > 0 else "up"

    def _start_reveal(self) -> None:
        self.approaching = False
        self.monster.vx = 0.0
        self.monster.vy = 0.0
        self.monster.is_moving = False
        self.monster.change_animation(f"catching-{self.monster.direction}")
        self.monster.current_animation.reset()
