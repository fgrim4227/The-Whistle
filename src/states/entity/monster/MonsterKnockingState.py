import math
import random

import settings
from src.commands import CHASE, PATROL
from src.states.entity.monster.MonsterBaseState import MonsterBaseState


class MonsterKnockingState(MonsterBaseState):
    """
    Knocks loudly on a door before entering the target room, giving the
    player a warning and time to hide.
    """
    def enter(self, door, target_room: str, *args, **kwargs) -> None:
        self.door = door
        self.target_room = target_room
        self.timer = random.randint(2, 3)
        self.monster.vx = 0.0
        self.monster.vy = 0.0
        self.monster.is_moving = False
        self.monster.change_animation(f"idle-{self.monster.direction}")
        settings.play_sound("knock_door", loops=0, volume=1.0, channel_name="knock")

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "FirstRoom"

        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            dist = math.hypot(player.x - self.monster.x, player.y - self.monster.y)
            if self.monster.can_detect_player(player, house) or dist < 140.0:
                CHASE(self.monster)
                return

        self.timer -= dt
        if self.timer <= 0.0:
            self.monster.enter_room(
                self.target_room,
                self.door.target_spawn_x,
                self.door.target_spawn_y,
                house.rooms.get(self.target_room),
            )

            if self.monster.current_room_name == player_room_name and self.monster.can_detect_player(player, house):
                CHASE(self.monster)
            else:
                PATROL(self.monster)
