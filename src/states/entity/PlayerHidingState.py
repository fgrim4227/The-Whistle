from src.states.entity.PlayerBaseState import PlayerBaseState


class PlayerHidingState(PlayerBaseState):
    def enter(self, *args, **kwargs) -> None:
        self.player.vx = 0.0
        self.player.vy = 0.0
