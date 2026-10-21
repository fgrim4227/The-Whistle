import settings
from src.states.entity.player.PlayerBaseState import PlayerBaseState


class PlayerHidingState(PlayerBaseState):
    def enter(self, *args, **kwargs) -> None:
        self.player.vx = 0.0
        self.player.vy = 0.0
        vol = getattr(settings, "PLAYER_HIDDEN_BREATH_VOLUME", 0.35)
        ch = settings.play_sound(
            "hidden_breathing",
            loops=-1,
            volume=vol,
            channel_name="player_hidden_breath",
        )
        if ch:
            ch.set_volume(vol)

    def exit(self) -> None:
        settings.stop_channel("player_hidden_breath")
