"""
BaseMinigame: Abstract base class for all real-time in-game minigames.
Minigames run as active overlays on top of PlayState without freezing the game world or El Silbón.
"""

from typing import Any, Callable, Optional
import pygame

import settings


class BaseMinigame:
    def __init__(
        self,
        play_state: Any,
        target_object: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
    ) -> None:
        self.play_state = play_state
        self.target_object = target_object
        self.on_success = on_success
        self.on_fail = on_fail

        self.is_active = True
        self.is_completed = False
        self.alert_timer = 0.0

    def close(self) -> None:
        """Deactivates and closes the minigame, returning full control to the player."""
        self.is_active = False
        if hasattr(self.play_state, "active_minigame") and self.play_state.active_minigame is self:
            self.play_state.active_minigame = None
        if hasattr(self.play_state, "player"):
            self.play_state.player.sync_movement_keys()

    def alert_monster(self, radius: float = 1000, sound_name: Optional[str] = None, volume: float = 1.0) -> None:
        """
        Emits acoustic disturbance that alerts El Silbón to investigate Andreas's current position.
        Optionally plays a loud sound effect on the dedicated minigame audio channel.
        """
        if sound_name:
            settings.play_sound(sound_name, loops=0, volume=volume, channel_name="minigame")

        if hasattr(self.play_state, "monster") and hasattr(self.play_state, "player"):
            px, py = self.play_state.player.get_center()
            self.play_state.monster.hear_noise(px, py, radius=radius)

    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handles raw pygame events.
        Return True if event was consumed by the minigame.
        """
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_e):
            self.close()
            return True
        return False

    def handle_action(self, input_id: str, input_data: Any) -> bool:
        """
        Handles Gale InputHandler action events.
        Return True if action was consumed by the minigame.
        """
        if getattr(input_data, "pressed", True):
            if input_id in ("quit", "pause", "escape"):
                self.close()
                return True
        return False

    def update(self, dt: float) -> None:
        """Updates internal timers, animations, physics, and state checks."""
        if self.alert_timer > 0.0:
            self.alert_timer = max(0.0, self.alert_timer - dt)

    def render(self, surface: pygame.Surface) -> None:
        """Renders the minigame interface, dials, cables, or meters on screen."""
        pass
