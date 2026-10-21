import settings
from src.states.entity.player.PlayerBaseState import PlayerBaseState


class PlayerHidingState(PlayerBaseState):
    def enter(self, *args, **kwargs) -> None:
        self.player.vx = 0.0
        self.player.vy = 0.0
        settings.play_sound(
            "hidden_breathing",
            loops=-1,
            volume=getattr(settings, "PLAYER_HIDDEN_BREATH_VOLUME", 0.8),
            channel_name="player_hidden_breath",
        )

    def exit(self) -> None:
        settings.stop_channel("player_hidden_breath")
