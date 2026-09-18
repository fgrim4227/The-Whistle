import math

import settings
from src.commands import PATROL
from src.systems import Pathfinding
from src.states.entity.monster.MonsterBaseState import MonsterBaseState

# Value that the monster will continue to chase the player after losing sight of them
LOST_SIGHT_TIMEOUT = 2.5

# How far the remembered player position has to drift before the route
# gets recalculated. A fresh route can start off in a slightly different
# direction than the one it replaces, so recalculating too eagerly -- as
# the player keeps shifting position while being chased up close -- shows
# up as the monster's walking animation flicking between directions.
# Two grid cells gives it room to keep committing to a route a little
# longer before asking for a new one.
REPATH_DIST = 32.0

WAYPOINT_ARRIVAL_DIST = 10.0


class MonsterChaseState(MonsterBaseState):
    """Active pursuit of the player."""

    def enter(self, *args, **kwargs) -> None:
        self.monster.speed = settings.MONSTER_CHASE_SPEED
        self.lost_sight_timer = 0.0
        self.last_seen_x = self.monster.x
        self.last_seen_y = self.monster.y
        self.path = []
        self.path_index = 0
        self.path_target_x = None
        self.monster.change_animation(f"run-{self.monster.direction}")
        self.path_target_y = None

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"

        if self.monster.current_room_name != player_room_name:
            PATROL(self.monster)
            return

        if player.is_hidden:
            PATROL(self.monster)
            return

        if self.monster.can_detect_player(player, house):
            self.lost_sight_timer = 0.0
            # Update the last known position of the player (if the monster can see the player
            # the last known position is the current position of the player)
            self.last_seen_x, self.last_seen_y = player.get_center()
        else:
            #lost sight of the player, start counting down to give up
            self.lost_sight_timer += dt
            if self.lost_sight_timer >= LOST_SIGHT_TIMEOUT:
                self.monster.change_state("stalking", target_x=self.last_seen_x, target_y=self.last_seen_y)
                return

        current_room = house.rooms.get(self.monster.current_room_name)
        obstacles = current_room.get_obstacles() if current_room else []

        # Recompute the route only when the remembered player position has
        # actually moved, or the current one has been fully walked -- same
        # convention as patrol/stalking/moving_to_door -- instead of asking
        # for a brand new one every frame regardless of whether anything changed.
        target_moved = (
            self.path_target_x is None
            or math.hypot(self.last_seen_x - self.path_target_x, self.last_seen_y - self.path_target_y) > REPATH_DIST
        )
        if current_room and (target_moved or self.path_index >= len(self.path)):
            route_width, min_route_width = self.monster.get_route_widths()
            self.path = Pathfinding.find_path(
                current_room, self.monster.get_collision_center(), (self.last_seen_x, self.last_seen_y),
                entity_width=route_width, min_entity_width=min_route_width
            )
            self.path_index = 0
            self.path_target_x, self.path_target_y = self.last_seen_x, self.last_seen_y

        if self.path_index < len(self.path):
            step_x, step_y = self.path[self.path_index]
            self.monster.move_towards(step_x, step_y, obstacles, dt)

            mx, my = self.monster.get_collision_center()
            if math.hypot(step_x - mx, step_y - my) < WAYPOINT_ARRIVAL_DIST:
                self.path_index += 1
        else:
            # No route found, or the route has been fully walked and the
            # remaining distance to the target itself is what's left to close.
            self.monster.move_towards(self.last_seen_x, self.last_seen_y, obstacles, dt)
