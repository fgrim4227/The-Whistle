"""
Note reader modal state mounted on top of the StateStack (Slender-style parchment notes).
"""

from typing import Optional, Callable
import pygame
from gale.input_handler import InputData
from gale.state import BaseState

import settings
from src.i18n import t


class NoteState(BaseState):
    def __init__(
        self,
        state_machine,
        note_title_key: str,
        note_body_key: str,
        attached_item: Optional[str] = None,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(state_machine)
        self.note_title_key = note_title_key
        self.note_body_key = note_body_key
        self.attached_item = attached_item
        self.on_close = on_close

    def exit(self) -> None:
        if self.on_close:
            callback = self.on_close
            self.on_close = None
            callback()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("interact", "action", "enter", "quit", "pause", "objectives"):
            self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        # 1. Dark atmosphere vignette overlay
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((4, 4, 8, 225))
        surface.blit(overlay, (0, 0))

        # 2. Aged parchment sheet
        paper_rect = pygame.Rect(44, 18, settings.VIRTUAL_WIDTH - 88, settings.VIRTUAL_HEIGHT - 36)
        pygame.draw.rect(surface, (232, 222, 195), paper_rect, border_radius=4)
        pygame.draw.rect(surface, (110, 80, 45), paper_rect, width=2, border_radius=4)

        # Subtle paper margin line
        pygame.draw.rect(surface, (215, 202, 175), paper_rect.inflate(-8, -8), width=1, border_radius=2)

        # 3. Note Title
        title_text = t(self.note_title_key)
        title_surf = settings.FONTS.get("note_title", settings.FONTS["medium"]).render(title_text, True, (65, 35, 15))
        surface.blit(title_surf, (paper_rect.centerx - title_surf.get_width() // 2, paper_rect.top + 12))

        # Divider line
        div_y = paper_rect.top + 16 + title_surf.get_height()
        pygame.draw.line(surface, (140, 110, 80), (paper_rect.left + 16, div_y), (paper_rect.right - 16, div_y), 1)

        # 4. Note Body with automatic word wrapping
        body_text = t(self.note_body_key)
        font_body = settings.FONTS.get("note_body", settings.FONTS["small"])
        max_line_w = paper_rect.width - 36

        words = body_text.split(" ")
        lines = []
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            if font_body.size(test_line)[0] <= max_line_w:
                cur_line.append(word)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))

        cur_y = div_y + 10
        for line in lines:
            line_surf = font_body.render(line, True, (45, 32, 22))
            surface.blit(line_surf, (paper_rect.left + 18, cur_y))
            cur_y += line_surf.get_height() + 3

        # 5. Attached Item Indicator (if any)
        if self.attached_item:
            att_y = paper_rect.bottom - 42
            item_name = t(f"item_{self.attached_item}")
            att_badge = f"{t('note_with_object')} {item_name}"
            att_surf = settings.FONTS["small"].render(att_badge, True, (130, 85, 20))
            att_rect = att_surf.get_rect(centerx=paper_rect.centerx, top=att_y)
            pygame.draw.rect(surface, (245, 235, 210), att_rect.inflate(10, 4), border_radius=2)
            pygame.draw.rect(surface, (150, 110, 40), att_rect.inflate(10, 4), width=1, border_radius=2)
            surface.blit(att_surf, att_rect)

        # 6. Close prompt hint
        close_hint = settings.FONTS["small"].render(t("note_close_hint"), True, (120, 100, 75))
        surface.blit(close_hint, (paper_rect.centerx - close_hint.get_width() // 2, paper_rect.bottom - 20))
