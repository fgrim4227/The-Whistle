"""
Victory state upon unlocking the exit door and escaping into the dark forest.
"""

import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from gale.state import BaseState


class VictoryState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.timer = 0.0

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("enter", "action", "interact", "quit"):
            while len(self.state_machine.states) > 1:
                self.state_machine.pop()

    def update(self, dt: float) -> None:
        self.timer += dt

    def render(self, surface: pygame.Surface) -> None:
        # Deep blue dawn atmosphere
        surface.fill((15, 25, 35))

        title = settings.FONTS["large"].render(t("victory_title"), True, settings.COLOR_GOLD)
        quote = settings.FONTS["small"].render(t("victory_quote"), True, settings.COLOR_WHITE)
        hint = settings.FONTS["medium"].render(t("victory_restart"), True, settings.COLOR_GRAY)

        surface.blit(title, (settings.VIRTUAL_WIDTH // 2 - title.get_width() // 2, 80))
        surface.blit(quote, (settings.VIRTUAL_WIDTH // 2 - quote.get_width() // 2, 130))
        surface.blit(hint, (settings.VIRTUAL_WIDTH // 2 - hint.get_width() // 2, 190))
