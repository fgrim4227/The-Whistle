import math
import random

import settings
from src.commands import CHASE, PATROL
from src.states.entity.MonsterBaseState import MonsterBaseState


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
        self.monster.change_animation("idle")
        settings.play_sound("knock_door", loops=0, volume=1.0, channel_name="knock")

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "FirstRoom"

        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            dist = math.hypot(player.x - self.monster.x, player.y - self.monster.y)
            if self.monster.can_detect_player(player) or dist < 140.0:
                CHASE(self.monster)
                return

        self.timer -= dt
        if self.timer <= 0.0:
            self.monster.current_room_name = self.target_room
            self.monster.x = self.door.target_spawn_x
            self.monster.y = self.door.target_spawn_y
            self.monster.current_wp_idx = 0

            if self.monster.current_room_name == player_room_name and self.monster.can_detect_player(player):
                CHASE(self.monster)
            else:
                PATROL(self.monster)
