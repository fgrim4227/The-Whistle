"""
Pause modal state mounted on top of the StateStack.
"""

import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from src.states.BaseState import BaseState


class PauseState(BaseState):
    def __init__(self, state_stack) -> None:
        super().__init__(state_stack)
        self.selected_index = 0

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("pause", "quit"):
            self.state_stack.pop()
        elif input_id == "move_up":
            self.selected_index = (self.selected_index - 1) % 2
        elif input_id == "move_down":
            self.selected_index = (self.selected_index + 1) % 2
        elif input_id == "enter":
            if self.selected_index == 0:
                self.state_stack.pop()
            elif self.selected_index == 1:
                # Return to Main Menu: pop stack down to StartState
                while len(self.state_stack.states) > 1:
                    self.state_stack.pop()

    def render(self, surface: pygame.Surface) -> None:
        # Translucent overlay over the paused game world
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title_surf = settings.FONTS["large"].render(t("pause_title"), True, settings.COLOR_GOLD)
        surface.blit(title_surf, (settings.VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 70))

        options = [t("pause_resume"), t("pause_menu")]
        for i, opt in enumerate(options):
            is_selected = (i == self.selected_index)
            color = settings.COLOR_GOLD if is_selected else settings.COLOR_WHITE
            prefix = "► " if is_selected else "  "
            surf = settings.FONTS["medium"].render(prefix + opt, True, color)
            surface.blit(surf, (settings.VIRTUAL_WIDTH // 2 - surf.get_width() // 2, 130 + i * 30))
