import math

import settings
from src.commands import CHASE, PATROL
from src.states.entity.monster.MonsterBaseState import MonsterBaseState
from src.systems import Pathfinding

WAYPOINT_ARRIVAL_DIST = 10.0

class MonsterInvestigateState(MonsterBaseState):
    """Investigates a thrown object's noise or disturbance."""

    def enter(self, target_x: float, target_y: float, *args, **kwargs) -> None:
        self.target_x = target_x
        self.target_y = target_y
        self.timer = 4.0
        self.monster.speed = settings.MONSTER_PATROL_SPEED
        self.path = []
        self.path_index = 0
        self.path_computed = False
        self.monster.change_animation(f"walk-{self.monster.direction}")

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"
        if self.monster.current_room_name != player_room_name:
            #I think we should cheat a little and teleport him to the player's room or get him closer
            PATROL(self.monster)
            return

        if self.monster.can_detect_player(player, house):
            CHASE(self.monster)
            return

        self.timer -= dt
        mx, my = self.monster.get_collision_center()
        dist = math.hypot(self.target_x - mx, self.target_y - my)
        if dist < 16.0 or self.timer <= 0.0:
            PATROL(self.monster)
            return

        current_room = house.rooms.get(self.monster.current_room_name)
        obstacles = current_room.get_obstacles() if current_room else []

        # The noise came from one fixed spot, so the route to it is worked
        # out once and then walked, not asked for again every frame.
        if not self.path_computed and current_room:
            route_width, min_route_width = self.monster.get_route_widths()
            self.path = Pathfinding.find_path(
                current_room, self.monster.get_collision_center(), (self.target_x, self.target_y),
                entity_width=route_width, min_entity_width=min_route_width
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
            # Either no route exists or it has been walked to the end; close
            # whatever gap is left to the noise directly.
            self.monster.move_towards(self.target_x, self.target_y, obstacles, dt)

