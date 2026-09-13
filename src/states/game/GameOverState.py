"""
Game Over / Jumpscare state when caught by El Silbón.
Alternates between jumpscare imagery (silbon_attack, red flash screen, and subliminal silbon_sad)
with violent screen shake and seamless background fills, backed by dual composite jumpscare audio.
"""

import math
import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from gale.state import BaseState


class GameOverState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.timer = 0.0
        self.jumpscare_duration = 2.4
        self.margin = 24

        # Target dimensions with margin padding for screen shake without edge clipping
        target_w = settings.VIRTUAL_WIDTH + self.margin * 2
        target_h = settings.VIRTUAL_HEIGHT + self.margin * 2

        # Scale jumpscare imagery
        raw_attack = settings.TEXTURES.get("silbon_attack")
        raw_sad = settings.TEXTURES.get("silbon_sad")
        raw_red = settings.TEXTURES.get("silbon_red")

        self.img_attack = (
            pygame.transform.scale(raw_attack, (target_w, target_h))
            if raw_attack
            else None
        )
        self.img_sad = (
            pygame.transform.scale(raw_sad, (target_w, target_h))
            if raw_sad
            else None
        )
        self.img_red = (
            pygame.transform.scale(raw_red, (target_w, target_h))
            if raw_red
            else None
        )

        # Fallback for red flash if image is missing
        if not self.img_red:
            self.img_red = pygame.Surface((target_w, target_h))
            self.img_red.fill(settings.COLOR_SILBON_RED)

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
                while len(self.state_machine.states) > 1:
                    self.state_machine.pop()

    def update(self, dt: float) -> None:
        self.timer += dt

    def render(self, surface: pygame.Surface) -> None:
        if self.timer < self.jumpscare_duration:
            # Violent screen shake with frequency decay
            shake_amp = 8.0
            shake_x = int(math.sin(self.timer * 72.0) * shake_amp)
            shake_y = int(math.cos(self.timer * 64.0) * shake_amp)

            # Rapid 12-step alternation:
            # - silbon_attack: dominant terror image (steps 0, 1, 3, 4, 8, 9, 10)
            # - silbon_red: pure red background flash (#b80200) cushioning transitions (steps 2, 5, 7, 11)
            # - silbon_sad: rare subliminal horror flash (step 6 only)
            step = int(self.timer * 16.0) % 12
            if step in (0, 1, 3, 4, 8, 9, 10):
                active_img = self.img_attack
                bg_color = settings.COLOR_BLACK
            elif step == 6:
                active_img = self.img_sad
                bg_color = settings.COLOR_SILBON_RED
            else:
                active_img = self.img_red
                bg_color = settings.COLOR_SILBON_RED

            # 1. Fill background with matching palette to eliminate letterbox/shake artifacts
            surface.fill(bg_color)

            # 2. Draw active jumpscare image offset by screen shake and margin
            if active_img:
                surface.blit(active_img, (-self.margin + shake_x, -self.margin + shake_y))
        else:
            # Black Game Over screen
            surface.fill(settings.COLOR_BLACK)

            title = settings.FONTS["large"].render(t("gameover_title"), True, settings.COLOR_BLOOD_RED)
            quote = settings.FONTS["small"].render(t("gameover_quote"), True, settings.COLOR_GRAY)
            restart = settings.FONTS["medium"].render(t("gameover_restart"), True, settings.COLOR_WHITE)

            surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, 80))
            surface.blit(quote, (settings.VIRTUAL_WIDTH // 2 - quote.get_width() // 2, 130))
            surface.blit(restart, (settings.VIRTUAL_WIDTH // 2 - restart.get_width() // 2, 190))
