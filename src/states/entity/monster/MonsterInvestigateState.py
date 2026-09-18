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
        player_room_name = house.current_room.name if house.current_room else "FirstRoom"
        if self.monster.current_room_name != player_room_name:
            # Alien: Isolation style - When a disturbance is heard in another room (e.g. failed minigame),
            # El Silbón stalks directly to the door outside the player's room and knocks loudly,
            # giving the player 3-4 seconds of pure panic to hide before bursting in.
            target_room = house.rooms.get(player_room_name)
            candidate_doors = []
            if target_room:
                for d in getattr(target_room, "doors", []):
                    outside_room_name = d.target_room_name
                    outside_room = house.rooms.get(outside_room_name)
                    if not outside_room:
                        continue
                    for rd in getattr(outside_room, "doors", []):
                        if rd.target_room_name in (player_room_name, getattr(target_room, "display_name", "")):
                            if rd.is_exit_door or rd.is_barred or rd.is_locked or getattr(rd, "is_bolted", False):
                                continue
                            if getattr(rd, "planks_remaining", 0) > 0:
                                continue
                            candidate_doors.append((outside_room_name, rd))
                            break

            if candidate_doors:
                # Prefer a door in the monster's current room if directly adjacent
                matching = [c for c in candidate_doors if c[0] == self.monster.current_room_name]
                chosen_room_name, chosen_door = matching[0] if matching else candidate_doors[0]

                self.monster.current_room_name = chosen_room_name
                self.monster.x = float(chosen_door.x)
                self.monster.y = float(chosen_door.y)
                self.monster.vx = 0.0
                self.monster.vy = 0.0
                self.monster.is_moving = False
                self.monster.change_state("knocking", door=chosen_door, target_room=player_room_name)
                return

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

