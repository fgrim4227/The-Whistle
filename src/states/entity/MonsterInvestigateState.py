import math

import settings
from src.states.entity.MonsterBaseState import MonsterBaseState


class MonsterInvestigateState(MonsterBaseState):
    """Investigates a thrown object's noise or disturbance."""

    def enter(self, target_x: float, target_y: float, *args, **kwargs) -> None:
        self.target_x = target_x
        self.target_y = target_y
        self.timer = 4.0
        self.monster.speed = settings.MONSTER_PATROL_SPEED

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"
        if self.monster.current_room_name != player_room_name:
            self.monster.change_state("patrol")
            return

        if self.monster.can_detect_player(player):
            self.monster.change_state("chase")
            return

        self.timer -= dt
        mx, my = self.monster.get_center()
        dist = math.hypot(self.target_x - mx, self.target_y - my)
        if dist < 16.0 or self.timer <= 0.0:
            self.monster.change_state("patrol")
            return

        current_room = house.rooms.get(self.monster.current_room_name)
        obstacles = current_room.get_obstacles() if current_room else []
        self.monster.move_towards(self.target_x, self.target_y, obstacles, dt)
