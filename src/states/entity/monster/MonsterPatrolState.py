import math
import random
from typing import Optional, Tuple

import settings
from src.systems import Pathfinding
from src.states.entity.monster.MonsterBaseState import MonsterBaseState

# Chance, each time it reaches a patrol waypoint, that it pauses to
# breathe instead of moving straight on to the next one.
BREATHING_CHANCE = 0.2


class MonsterPatrolState(MonsterBaseState):
    """
    Patrols between waypoints within the current room.
    If the player is in another room or hidden, counts down to change rooms and leaves.
    """
    def enter(self, *args, **kwargs) -> None:
        self.monster.speed = settings.MONSTER_PATROL_SPEED
        self.room_change_cooldown = random.uniform(2, 4)
        self.suspicion_timer = 0.0
        self.hidden_leave_timer = random.uniform(6, 8)
        self.path = []
        self.path_index = 0
        self.path_target_idx = None
        self.monster.change_animation(f"walk-{self.monster.direction}")

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"
        monster_room_name = self.monster.current_room_name
        current_room = house.rooms.get(monster_room_name)

        if monster_room_name == player_room_name:
            if player.is_hidden:
                self.hidden_leave_timer -= dt
                if self.hidden_leave_timer <= 0.0:
                    self._leave_room(house)
                    return
                self._patrol_room(current_room, dt, avoid_pos=(player.x, player.y))
                return

            if self.monster.can_detect_player(player, house):
                self.suspicion_timer += dt
                if self.suspicion_timer >= 0.3:
                    px, py = player.get_center()
                    self.monster.change_state("stalking", target_x=px, target_y=py)
                    return
            else:
                self.suspicion_timer = max(0.0, self.suspicion_timer - dt * 1.5)

            self._patrol_room(current_room, dt)

        else:
            self.room_change_cooldown -= dt
            if self.room_change_cooldown <= 0.0:
                self.room_change_cooldown = random.uniform(5, 8)
                self._leave_room(house, target_room_preference=self.monster.director_room_hint)

    def _patrol_room(self, current_room, dt: float, avoid_pos: Optional[Tuple[float, float]] = None) -> None:

        if not current_room:
            return

        if not current_room.patrol_waypoints:
            current_room.patrol_waypoints = Pathfinding.sample_walkable_points(
                current_room, entity_width=self.monster.get_route_widths()[1]
            )
            if not current_room.patrol_waypoints:
                return

        wp = current_room.patrol_waypoints[self.monster.current_wp_idx % len(current_room.patrol_waypoints)]

        if avoid_pos:
            dist_to_avoid = math.hypot(wp[0] - avoid_pos[0], wp[1] - avoid_pos[1])
            if dist_to_avoid < 90.0 and len(current_room.patrol_waypoints) > 1:
                self.monster.current_wp_idx = (self.monster.current_wp_idx + 1) % len(current_room.patrol_waypoints)
                wp = current_room.patrol_waypoints[self.monster.current_wp_idx % len(current_room.patrol_waypoints)]

        self.monster.target_x, self.monster.target_y = wp

        # Only recompute the route when the target waypoint itself
        # changed (arrival or an avoid_pos skip), not every frame.
        if self.path_target_idx != self.monster.current_wp_idx or not self.path:
            route_width, min_route_width = self.monster.get_route_widths()
            self.path = Pathfinding.find_path(
                current_room, self.monster.get_collision_center(), wp,
                entity_width=route_width, min_entity_width=min_route_width
            )

            self.path_index = 0
            self.path_target_idx = self.monster.current_wp_idx

        if self.path_index >= len(self.path):
            self.monster.current_wp_idx = (self.monster.current_wp_idx + 1) % len(current_room.patrol_waypoints)
            if random.random() < BREATHING_CHANCE:
                self.monster.change_state("breathing")
            return

        obstacles = current_room.get_obstacles()
        step_x, step_y = self.path[self.path_index]
        self.monster.move_towards(step_x, step_y, obstacles, dt)

        mx, my = self.monster.get_collision_center()
        if math.hypot(step_x - mx, step_y - my) < 10:
            self.path_index += 1


    def _leave_room(self, house, target_room_preference: Optional[str] = None) -> None:
        current_room = house.rooms.get(self.monster.current_room_name)
        if not current_room:
            return

        valid_doors = []
        for d in current_room.doors:
            if d.is_exit_door or d.is_barred or d.is_locked or getattr(d, "is_bolted", False):
                continue
            if getattr(d, "planks_remaining", 0) > 0:
                continue
            if d.target_room_name not in house.rooms:
                continue
            # Check if door is barred or locked from the opposite side
            target_rm = house.rooms.get(d.target_room_name)
            reciprocal_blocked = False
            if target_rm:
                current_names = {current_room.name}
                if getattr(current_room, "display_name", None):
                    current_names.add(current_room.display_name)
                for k, v in getattr(house, "rooms", {}).items():
                    if v is current_room:
                        current_names.add(k)
                for rd in getattr(target_rm, "doors", []):
                    if rd.target_room_name in current_names:
                        if rd.is_barred or rd.is_locked or getattr(rd, "is_bolted", False) or getattr(rd, "planks_remaining", 0) > 0:
                            reciprocal_blocked = True
                            break
            if reciprocal_blocked:
                continue
            valid_doors.append(d)
        if not valid_doors:
            return

        chosen_door = None
        if target_room_preference:
            chosen_door = next(
                (d for d in valid_doors if d.target_room_name == target_room_preference),
                None
            )

        # A suggestion is spent the moment a door gets picked, matched or
        # not, so it nudges one decision rather than biasing every future one.
        self.monster.director_room_hint = None

        if not chosen_door and valid_doors:
            chosen_door = random.choice(valid_doors)
            
        if chosen_door:
            self.monster.change_state("moving_to_door", door=chosen_door, target_room=chosen_door.target_room_name)

