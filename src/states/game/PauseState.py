"""
Pause modal state mounted on top of the StateStack.
"""

from typing import Callable, Optional
import pygame
from gale.input_handler import InputData
from gale.state import BaseState

import settings
from src.i18n import t


class PauseState(BaseState):
    def __init__(self, state_machine, on_close: Optional[Callable[[], None]] = None) -> None:
        super().__init__(state_machine)
        self.selected_index = 0
        self.on_close = on_close
        self.show_instructions = False

    def exit(self) -> None:
        if self.on_close:
            callback = self.on_close
            self.on_close = None
            callback()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if self.show_instructions:
            if input_id in ("enter", "quit", "interact", "pause"):
                self.show_instructions = False
            return

        if input_id in ("pause", "quit"):
            self.state_machine.pop()
        elif input_id == "move_up":
            self.selected_index = (self.selected_index - 1) % 3
        elif input_id == "move_down":
            self.selected_index = (self.selected_index + 1) % 3
        elif input_id == "enter":
            if self.selected_index == 0:
                self.state_machine.pop()
            elif self.selected_index == 1:
                self.show_instructions = True
            elif self.selected_index == 2:
                # Return to Main Menu: pop stack down to StartState
                while len(self.state_machine.states) > 1:
                    self.state_machine.pop()

    def _render_instructions(self, surface: pygame.Surface) -> None:
        # Modal instructions dialog matching StartState
        modal_rect = pygame.Rect(40, 22, settings.VIRTUAL_WIDTH - 80, settings.VIRTUAL_HEIGHT - 44)
        pygame.draw.rect(surface, (20, 20, 30), modal_rect, border_radius=8)
        pygame.draw.rect(surface, settings.COLOR_DARK_RED, modal_rect, width=2, border_radius=8)

        title = settings.FONTS["medium"].render(t("menu_instructions"), True, settings.COLOR_GOLD)
        surface.blit(title, (modal_rect.centerx - title.get_width() // 2, modal_rect.top + 10))

        lines = [
            t("inst_move"),
            t("inst_flashlight"),
            t("inst_interact"),
            t("inst_throw"),
            t("inst_objectives"),
            t("inst_pause"),
            t("inst_run"),
            t("inst_fullscreen"),
            t("inst_exit"),
            "",
            t("inst_warning"),
            t("inst_back"),
        ]

        for idx, line in enumerate(lines):
            color = settings.COLOR_GOLD if idx == 10 else settings.COLOR_WHITE
            line_surf = settings.FONTS["small"].render(line, True, color)
            surface.blit(line_surf, (modal_rect.left + 25, modal_rect.top + 36 + idx * 16))

    def render(self, surface: pygame.Surface) -> None:
        # Translucent overlay over the paused game world
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        if self.show_instructions:
            self._render_instructions(surface)
            return

        title_surf = settings.FONTS["large"].render(t("pause_title"), True, settings.COLOR_GOLD)
        surface.blit(title_surf, (settings.VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 60))

        options = [t("pause_resume"), t("pause_instructions"), t("pause_menu")]
        for i, opt in enumerate(options):
            is_selected = (i == self.selected_index)
            color = settings.COLOR_GOLD if is_selected else settings.COLOR_WHITE
            prefix = "► " if is_selected else "  "
            surf = settings.FONTS["medium"].render(prefix + opt, True, color)
            surface.blit(surf, (settings.VIRTUAL_WIDTH // 2 - surf.get_width() // 2, 115 + i * 28))
