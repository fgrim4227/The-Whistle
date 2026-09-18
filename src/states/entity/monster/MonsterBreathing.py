import random

import settings
from src.commands import CHASE, PATROL
from src.states.entity.monster.MonsterBaseState import MonsterBaseState

# How often the breathing sound repeats while paused in this state.
BREATH_SOUND_INTERVAL = 2.0


class MonsterBreathingState(MonsterBaseState):
    """
    Just an idle animation, standing completely still as if listening or
    thinking, breathing loudly the whole time. Used whenever the monster
    isn't actively chasing the player.
    """
    def enter(self, *args, **kwargs) -> None:
        self.timer = random.randint(2, 3)
        self.breath_timer = 0.0
        self.monster.vx = 0.0
        self.monster.vy = 0.0
        self.monster.is_moving = False
        self.monster.change_animation(f"breathing-{self.monster.direction}")

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"
        if self.monster.current_room_name == player_room_name and self.monster.can_detect_player(player, house):
            CHASE(self.monster)
            return

        self.breath_timer += dt
        if self.breath_timer >= BREATH_SOUND_INTERVAL:
            self.breath_timer = 0.0
            settings.play_sound("breathing", volume=0.6, channel_name="silbon_breath")

        self.timer -= dt
        if self.timer <= 0.0:
            PATROL(self.monster)
