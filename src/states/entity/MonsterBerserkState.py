import settings
from src.states.entity.MonsterBaseState import MonsterBaseState


class MonsterBerserkState(MonsterBaseState):
    """Enraged pursuit, triggered by a chance roll when hit by a thrown object."""

    def enter(self, *args, **kwargs) -> None:
        self.timer = 6.0
        self.monster.speed = settings.MONSTER_BERSERK_SPEED

    def process_ai(self, house, player, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            self.monster.change_state("patrol")
            return

        player_room_name = house.current_room.name if house.current_room else "bedroom"
        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            px, py = player.get_center()
            current_room = house.rooms.get(self.monster.current_room_name)
            obstacles = current_room.get_obstacles() if current_room else []
            self.monster.move_towards(px, py, obstacles, dt)
        else:
            self.monster.change_state("patrol")
