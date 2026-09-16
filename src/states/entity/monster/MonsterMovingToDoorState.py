import math

import settings
from src.commands import CHASE, PATROL
from src.states.entity.monster.MonsterBaseState import MonsterBaseState
from src.systems import Pathfinding


class _RoomWithoutDoor:
    """
    Envuelve una Room pero le esconde una puerta puntual a get_obstacles()
    -- así el A* no trata el propio destino (la puerta a la que vamos)
    como algo que bloquea el camino hacia ella.
    """
    def __init__(self, room, door_rect):
        self._room = room
        self._door_rect = door_rect
        self.width = room.width
        self.height = room.height

    def get_obstacles(self):
        return [obs for obs in self._room.get_obstacles() if not obs.colliderect(self._door_rect)]


class MonsterMovingToDoorState(MonsterBaseState):
    """
    Physically pathfinds and walks to a chosen door before transitioning
    rooms, instead of teleporting across the map.
    """
    def enter(self, door, target_room: str, *args, **kwargs) -> None:
        self.door = door
        self.target_room = target_room
        self.monster.speed = settings.MONSTER_PATROL_SPEED
        self.timeout = 8.0
        self.target_x = self.door.x + self.door.width / 2.0
        self.target_y = self.door.y + self.door.height / 2.0
        self.path = []
        self.path_index = 0
        self.path_computed = False

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "FirstRoom"
        current_room = house.rooms.get(self.monster.current_room_name)

        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            if self.monster.can_detect_player(player, house):
                CHASE(self.monster)
                return

        self.timeout -= dt

        door_rect = self.door.get_rect()
        raw_obstacles = current_room.get_obstacles() if current_room else []
        obstacles = [obs for obs in raw_obstacles if not obs.colliderect(door_rect)]

        # Door objective does'n change so the path to the door was only computed once
        if not self.path_computed and current_room:
            pathfinding_room = _RoomWithoutDoor(current_room, door_rect)
            route_width, min_route_width = self.monster.get_route_widths()
            self.path = Pathfinding.find_path(
                pathfinding_room, self.monster.get_collision_center(), (self.target_x, self.target_y),
                entity_width=route_width, min_entity_width=min_route_width
            )
            self.path_index = 0
            self.path_computed = True

        if self.path_index < len(self.path):
            step_x, step_y = self.path[self.path_index]
            self.monster.move_towards(step_x, step_y, obstacles, dt)
            mx, my = self.monster.get_collision_center()
            if math.hypot(step_x - mx, step_y - my) < 10:
                self.path_index += 1
        else:
            self.monster.move_towards(self.target_x, self.target_y, obstacles, dt)

        mx, my = self.monster.get_collision_center()
        dist_to_door = math.hypot(mx - self.target_x, my - self.target_y)

        if dist_to_door < 16 or self.timeout <= 0.0:
            if self.monster.current_room_name != player_room_name and self.target_room == player_room_name:
                # Approaching the player's own room from outside: knock first
                # instead of walking straight in, so the player has time to hide.
                self.monster.change_state("knocking", door=self.door, target_room=self.target_room)
            else:
                settings.play_sound("door_creak", loops=0, volume=3, channel_name="sfx")
                self.monster.current_room_name = self.target_room
                self.monster.x = self.door.target_spawn_x
                self.monster.y = self.door.target_spawn_y
                self.monster.current_wp_idx = 0
                self.monster.vx = 0.0
                self.monster.vy = 0.0
                self.monster.is_moving = False

                if self.monster.current_room_name == player_room_name and self.monster.can_detect_player(player, house):
                    CHASE(self.monster)
                else:
                    PATROL(self.monster)
