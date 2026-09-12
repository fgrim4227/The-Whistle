"""
Game Over / Jumpscare state when caught by El Silbón.
Plays both jumpscare sound effects (jumpscare1 + jumpscare2) simultaneously
for visceral acoustic terror.
"""

import pygame
import math
from gale.input_handler import InputData

import settings
from src.i18n import t
from src.states.BaseState import BaseState


class GameOverState(BaseState):
    def __init__(self, state_stack) -> None:
        super().__init__(state_stack)
        self.timer = 0.0
        self.jumpscare_duration = 2.2

    def enter(self, *args, **kwargs) -> None:
        self.timer = 0.0
        # Silence ambient music and whistling channels
        settings.stop_channel("ambience")
        settings.stop_channel("silbon_whistle")
        settings.stop_channel("silbon_breath")

        # Trigger both jumpscare sounds concurrently at maximum volume
        settings.play_sound("jumpscare1", loops=0, volume=1.0, channel_name="jumpscare1")
        settings.play_sound("jumpscare2", loops=0, volume=1.0, channel_name="jumpscare2")

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        # After the initial jumpscare shock, allow the player to restart
        if self.timer > self.jumpscare_duration:
            if input_id in ("enter", "action", "interact", "quit"):
                # Silence jumpscare and return to main menu
                settings.stop_channel("jumpscare1")
                settings.stop_channel("jumpscare2")
                while len(self.state_stack.states) > 1:
                    self.state_stack.pop()

    def update(self, dt: float) -> None:
        self.timer += dt

    def render(self, surface: pygame.Surface) -> None:
        if self.timer < self.jumpscare_duration:
            # Jumpscare screen shake and blood-red flashing effect
            shake_x = int(math.sin(self.timer * 60) * 6)
            shake_y = int(math.cos(self.timer * 60) * 6)
            intensity = int(180 + 75 * math.sin(self.timer * 35))
            surface.fill((intensity, 0, 0))

            center_x = settings.VIRTUAL_WIDTH // 2 + shake_x
            center_y = settings.VIRTUAL_HEIGHT // 2 + shake_y

            # Shadow silhouette of El Silbón lunging forward
            pygame.draw.circle(surface, (15, 5, 5), (center_x, center_y - 25), 55)
            # Wide-brim hat
            pygame.draw.ellipse(surface, (50, 40, 20), (center_x - 50, center_y - 65, 100, 20))
            # Glowing eyes
            eye_col = (255, 255, 220) if int(self.timer * 20) % 2 == 0 else (255, 20, 20)
            pygame.draw.circle(surface, eye_col, (center_x - 18, center_y - 30), 8)
            pygame.draw.circle(surface, eye_col, (center_x + 18, center_y - 30), 8)
            # Open terrifying maw
            pygame.draw.arc(surface, (220, 20, 20), (center_x - 26, center_y - 12, 52, 40), math.pi, 2 * math.pi, 5)
        else:
            # Black Game Over screen
            surface.fill(settings.COLOR_BLACK)

            title = settings.FONTS["large"].render(t("gameover_title"), True, settings.COLOR_BLOOD_RED)
            quote = settings.FONTS["small"].render(t("gameover_quote"), True, settings.COLOR_GRAY)
            restart = settings.FONTS["medium"].render(t("gameover_restart"), True, settings.COLOR_WHITE)

            surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, 80))
            surface.blit(quote, (settings.VIRTUAL_WIDTH // 2 - quote.get_width() // 2, 130))
            surface.blit(restart, (settings.VIRTUAL_WIDTH // 2 - restart.get_width() // 2, 190))
