"""
Objective notebook modal state mounted on top of the StateStack.
"""

import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from gale.state import BaseState


class ObjectiveState(BaseState):
    def __init__(self, state_machine, objectives_progress: dict = None) -> None:
        super().__init__(state_machine)
        self.objectives_progress = objectives_progress or {}

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("objectives", "quit", "pause", "enter", "interact"):
            self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        # Semi-transparent dark background overlay
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 200))
        surface.blit(overlay, (0, 0))

        # Antique paper / survivor notebook sheet
        book_rect = pygame.Rect(50, 25, settings.VIRTUAL_WIDTH - 100, settings.VIRTUAL_HEIGHT - 50)
        pygame.draw.rect(surface, (230, 220, 195), book_rect, border_radius=6)
        pygame.draw.rect(surface, (100, 70, 40), book_rect, width=3, border_radius=6)

        title = settings.FONTS["medium"].render(t("obj_title"), True, (50, 30, 15))
        surface.blit(title, (book_rect.centerx - title.get_width() // 2, book_rect.top + 16))

        pygame.draw.line(surface, (150, 120, 90), (book_rect.left + 20, book_rect.top + 42), (book_rect.right - 20, book_rect.top + 42), 2)

        objectives = [
            ("obj_1_flashlight", self.objectives_progress.get("flashlight", True)),
            ("obj_2_explore", self.objectives_progress.get("explore", True)),
            ("obj_3_crowbar", self.objectives_progress.get("crowbar", False)),
            ("obj_4_key", self.objectives_progress.get("key", False)),
            ("obj_5_escape", self.objectives_progress.get("escape", False)),
        ]

        for i, (key, done) in enumerate(objectives):
            color = (60, 120, 60) if done else (40, 40, 45)
            check = "[✓] " if done else "[ ] "
            text = check + t(key)
            surf = settings.FONTS["small"].render(text, True, color)
            surface.blit(surf, (book_rect.left + 25, book_rect.top + 55 + i * 28))

        close_hint = settings.FONTS["small"].render(t("obj_close"), True, (110, 90, 70))
        surface.blit(close_hint, (book_rect.centerx - close_hint.get_width() // 2, book_rect.bottom - 24))
