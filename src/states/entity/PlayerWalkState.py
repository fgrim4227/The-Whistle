from src.states.entity.PlayerBaseState import PlayerBaseState


class PlayerWalkState(PlayerBaseState):
    def enter(self, *args, **kwargs) -> None:
        self.player.change_animation(f"walk-{self.player.direction}")
