"""
Confirmation modal state mounted on top of the StateStack to prevent accidental quits.
"""

import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from typing import Callable, Optional
from gale.state import BaseState


class ConfirmationState(BaseState):
    def __init__(self, state_machine, on_close: Optional[Callable[[], None]] = None) -> None:
        super().__init__(state_machine)
        self.selected_index = 1
        self.on_close = on_close

    def exit(self) -> None:
        if self.on_close:
            callback = self.on_close
            self.on_close = None
            callback()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id == "quit":
            self.state_machine.pop()
        elif input_id == "move_up":
            self.selected_index = (self.selected_index - 1) % 2
        elif input_id == "move_down":
            self.selected_index = (self.selected_index + 1) % 2
        elif input_id == "enter":
            if self.selected_index == 0:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif self.selected_index == 1:
                self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        title_surf = settings.FONTS["large"].render(t("confirm_quit_title"), True, settings.COLOR_DARK_RED)
        surface.blit(title_surf, (settings.VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 70))

        options = [t("menu_yes"), t("menu_no")]
        for i, opt in enumerate(options):
            is_selected = (i == self.selected_index)
            color = settings.COLOR_GOLD if is_selected else settings.COLOR_WHITE
            prefix = "► " if is_selected else "  "
            surf = settings.FONTS["medium"].render(prefix + opt, True, color)
            surface.blit(surf, (settings.VIRTUAL_WIDTH // 2 - surf.get_width() // 2, 130 + i * 30))