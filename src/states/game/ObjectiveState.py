"""
Objective notebook modal state mounted on top of the StateStack.
"""

import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from typing import Callable, Optional
from gale.state import BaseState


class ObjectiveState(BaseState):
    def __init__(self, state_machine, objectives_progress: dict = None, on_close: Optional[Callable[[], None]] = None) -> None:
        super().__init__(state_machine)
        self.objectives_progress = objectives_progress or {}
        self.on_close = on_close

    def exit(self) -> None:
        if self.on_close:
            callback = self.on_close
            self.on_close = None
            callback()

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

        # Title
        title = settings.FONTS["medium"].render(t("obj_title"), True, (50, 30, 15))
        surface.blit(title, (book_rect.centerx - title.get_width() // 2, book_rect.top + 14))

        pygame.draw.line(surface, (150, 120, 90), (book_rect.left + 20, book_rect.top + 38), (book_rect.right - 20, book_rect.top + 38), 2)

        # Stage progression list: (key, is_done, is_unlocked)
        p = self.objectives_progress
        milestones = [
            ("obj_explore", bool(p.get("explore", False)), True),
            ("obj_kitchen_lockpick", bool(p.get("kitchen_lockpick", False)), bool(p.get("explore", False))),
            ("obj_dining_cabinet", bool(p.get("dining_cabinet", False)), bool(p.get("kitchen_lockpick", False))),
            ("obj_crowbar", bool(p.get("crowbar", False)), bool(p.get("dining_cabinet", False))),
            ("obj_fuse_power", bool(p.get("fuse_power", False)), bool(p.get("crowbar", False))),
            ("obj_master_safe", bool(p.get("master_safe", False)), bool(p.get("dining_cabinet", False))),
            ("obj_escape_forest", bool(p.get("escape", False)), bool(p.get("fuse_power", False) and p.get("master_safe", False))),
        ]

        # Find current primary objective (first unlocked and not yet completed)
        current_obj_key = "obj_explore"
        for key, done, unlocked in milestones:
            if unlocked and not done:
                current_obj_key = key
                break
        else:
            if all(done for _, done, _ in milestones):
                current_obj_key = "obj_escape_forest"

        # 1. Primary Active Mission Banner
        cur_header = settings.FONTS["small"].render(t("obj_current_task"), True, (120, 50, 20))
        surface.blit(cur_header, (book_rect.left + 25, book_rect.top + 46))

        cur_text = "▶ " + t(current_obj_key)
        cur_surf = settings.FONTS["medium"].render(cur_text, True, (160, 20, 10))
        surface.blit(cur_surf, (book_rect.left + 25, book_rect.top + 64))

        pygame.draw.line(surface, (180, 160, 130), (book_rect.left + 20, book_rect.top + 92), (book_rect.right - 20, book_rect.top + 92), 1)

        # 2. Checklist of discovered steps
        y_pos = book_rect.top + 102
        visible_count = 0
        for key, done, unlocked in milestones:
            if not unlocked and not done and key != current_obj_key:
                continue

            if done:
                color = (55, 115, 55)
                prefix = "[✓] "
            elif key == current_obj_key:
                color = (130, 40, 20)
                prefix = "[•] "
            else:
                color = (90, 85, 80)
                prefix = "[ ] "

            line_surf = settings.FONTS["small"].render(prefix + t(key), True, color)
            surface.blit(line_surf, (book_rect.left + 25, y_pos))
            y_pos += 22
            visible_count += 1
            if visible_count >= 5:
                break

        close_hint = settings.FONTS["small"].render(t("obj_close"), True, (110, 90, 70))
        surface.blit(close_hint, (book_rect.centerx - close_hint.get_width() // 2, book_rect.bottom - 20))
