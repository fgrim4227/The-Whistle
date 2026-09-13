import settings
from src.commands import PATROL
from src.states.entity.MonsterBaseState import MonsterBaseState


class MonsterChaseState(MonsterBaseState):
    """Active pursuit of the player."""

    def enter(self, *args, **kwargs) -> None:
        self.monster.speed = settings.MONSTER_CHASE_SPEED

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"

        if self.monster.current_room_name != player_room_name:
            PATROL(self.monster)
            return

        if player.is_hidden:
            PATROL(self.monster)
            return

        px, py = player.get_center()
        current_room = house.rooms.get(self.monster.current_room_name)
        obstacles = current_room.get_obstacles() if current_room else []
        self.monster.move_towards(px, py, obstacles, dt)
