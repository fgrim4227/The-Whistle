import math

import settings
from src.states.entity.MonsterBaseState import MonsterBaseState


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

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "FirstRoom"
        current_room = house.rooms.get(self.monster.current_room_name)

        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            if self.monster.can_detect_player(player):
                self.monster.change_state("chase")
                return

        self.timeout -= dt
        obstacles = current_room.get_obstacles() if current_room else []
        door_rect = self.door.get_rect()
        obstacles = [obs for obs in obstacles if not obs.colliderect(door_rect)]

        self.monster.move_towards(self.target_x, self.target_y, obstacles, dt)

        mx, my = self.monster.get_center()
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

                if self.monster.current_room_name == player_room_name and self.monster.can_detect_player(player):
                    self.monster.change_state("chase")
                else:
                    self.monster.change_state("patrol")
