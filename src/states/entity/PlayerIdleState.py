from src.states.entity.PlayerBaseState import PlayerBaseState


class PlayerIdleState(PlayerBaseState):
    def enter(self, *args, **kwargs) -> None:
        self.player.change_animation(f"idle-{self.player.direction}")
