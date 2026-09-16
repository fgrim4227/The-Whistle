from src.commands import BERSERK
from src.states.entity.monster.MonsterBaseState import MonsterBaseState


class MonsterStunnedState(MonsterBaseState):
    """Immobilized, triggered by a chance roll when hit by a thrown object. Enrages on recovery."""

    def enter(self, duration: float = 3.5, *args, **kwargs) -> None:
        self.timer = duration
        self.monster.vx = 0.0
        self.monster.vy = 0.0
        self.monster.is_moving = False
        self.monster.change_animation("idle")

    def process_ai(self, house, player, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            BERSERK(self.monster)
