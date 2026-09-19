"""
KeypadMinigame: 4-digit electronic / mechanical keypad security lock.
Used to unlock secret passages and emergency security doors.
Entering the incorrect passcode trips the security alarm and alerts El Silbón.
"""

from typing import Any, Callable, List, Optional
import pygame

import settings
from src.i18n import t
from src.minigames.BaseMinigame import BaseMinigame


class KeypadMinigame(BaseMinigame):
    def __init__(
        self,
        play_state: Any,
        target_object: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
        passcode: str = "1973",
    ) -> None:
        super().__init__(play_state, target_object, on_success, on_fail)
        self.passcode = str(passcode)
        self.code_length = len(self.passcode)
        self.entered_digits: List[str] = []

        # Keypad layout: 3x4 grid of buttons
        # 1 2 3
        # 4 5 6
        # 7 8 9
        # C 0 OK
        self.grid = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["C", "0", "OK"],
        ]
        self.selected_row = 0
        self.selected_col = 0

        self.feedback_message: str = ""
        self.feedback_timer: float = 0.0
        self.feedback_color: tuple = (220, 220, 220)
        self.cursor_blink_timer: float = 0.0

    def handle_input(self, event: pygame.event.Event) -> bool:
        if super().handle_input(event):
            return True

        if event.type == pygame.KEYDOWN:
            # Direct numeric keys
            if pygame.K_0 <= event.key <= pygame.K_9:
                digit = str(event.key - pygame.K_0)
                self._enter_digit(digit)
                return True
            elif pygame.K_KP0 <= event.key <= pygame.K_KP9:
                digit = str(event.key - pygame.K_KP0)
                self._enter_digit(digit)
                return True
            elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                self._backspace()
                return True
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if len(self.entered_digits) == self.code_length:
                    self._validate_passcode()
                else:
                    self._press_selected()
                return True
            elif event.key == pygame.K_SPACE:
                self._press_selected()
                return True
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_row = (self.selected_row - 1) % 4
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_row = (self.selected_row + 1) % 4
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_col = (self.selected_col - 1) % 3
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_col = (self.selected_col + 1) % 3
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True

        return False

    def handle_action(self, input_id: str, input_data: Any) -> bool:
        if super().handle_action(input_id, input_data):
            return True

        if getattr(input_data, "pressed", True):
            if input_id in ("action", "interact", "enter"):
                if len(self.entered_digits) == self.code_length:
                    self._validate_passcode()
                else:
                    self._press_selected()
                return True
            elif input_id in ("move_up", "up"):
                self.selected_row = (self.selected_row - 1) % 4
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True
            elif input_id in ("move_down", "down"):
                self.selected_row = (self.selected_row + 1) % 4
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True
            elif input_id in ("move_left", "left"):
                self.selected_col = (self.selected_col - 1) % 3
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True
            elif input_id in ("move_right", "right"):
                self.selected_col = (self.selected_col + 1) % 3
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.4, channel_name="minigame")
                return True

        return False

    def _enter_digit(self, digit: str) -> None:
        if len(self.entered_digits) < self.code_length:
            self.entered_digits.append(digit)
            settings.play_sound("minigame_dial_tick", loops=0, volume=0.8, channel_name="minigame")

    def _backspace(self) -> None:
        if self.entered_digits:
            self.entered_digits.pop()
            settings.play_sound("minigame_dial_tick", loops=0, volume=0.6, channel_name="minigame")

    def _press_selected(self) -> None:
        btn = self.grid[self.selected_row][self.selected_col]
        if btn == "C":
            if self.entered_digits:
                self.entered_digits.clear()
                settings.play_sound("minigame_dial_tick", loops=0, volume=0.7, channel_name="minigame")
        elif btn == "OK":
            self._validate_passcode()
        else:
            self._enter_digit(btn)

    def _validate_passcode(self) -> None:
        entered = "".join(self.entered_digits)
        if entered == self.passcode:
            self.is_completed = True
            self.feedback_message = t("keypad_success")
            self.feedback_color = (60, 240, 60)
            self.feedback_timer = 2.0
            settings.play_sound("minigame_unlock_click", loops=0, volume=1.0, channel_name="minigame")
            if self.on_success:
                self.on_success()
            self.close()
        else:
            self.entered_digits.clear()
            self.feedback_message = t("keypad_error")
            self.feedback_color = (255, 50, 50)
            self.feedback_timer = 2.5
            self.alert_monster(radius=900, sound_name="minigame_lock_forced", volume=1.0)
            if self.on_fail:
                self.on_fail()

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.is_active or self.is_completed:
            return

        self.cursor_blink_timer += dt * 3.0

        if self.feedback_timer > 0.0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)

    def render(self, surface: pygame.Surface) -> None:
        # 1. Dark Vignette Background
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((5, 5, 8, 220))
        surface.blit(overlay, (0, 0))

        # 2. Keypad Outer Box (industrial heavy security box)
        box_w = 210
        box_h = 240
        box_x = (settings.VIRTUAL_WIDTH - box_w) // 2
        box_y = (settings.VIRTUAL_HEIGHT - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        pygame.draw.rect(surface, (28, 27, 30), box_rect, border_radius=8)
        pygame.draw.rect(surface, (55, 53, 58), box_rect, width=3, border_radius=8)
        pygame.draw.rect(surface, (15, 14, 16), box_rect.inflate(-6, -6), width=1, border_radius=6)

        # Header Title
        title_font = settings.FONTS.get("dialogue", settings.FONTS["small"])
        title_surf = title_font.render(t("minigame_keypad_title"), True, (220, 200, 160))
        surface.blit(title_surf, (box_rect.centerx - title_surf.get_width() // 2, box_y + 10))

        # 3. LCD Display Screen
        screen_w = 170
        screen_h = 32
        screen_x = box_rect.centerx - screen_w // 2
        screen_y = box_y + 32
        screen_rect = pygame.Rect(screen_x, screen_y, screen_w, screen_h)

        pygame.draw.rect(surface, (12, 22, 14), screen_rect, border_radius=4)
        pygame.draw.rect(surface, (40, 70, 45), screen_rect, width=2, border_radius=4)

        # Display text: entered digits or placeholders
        small_font = settings.FONTS.get("small", settings.FONTS["small"])
        lcd_font = settings.FONTS.get("medium", settings.FONTS["small"])

        if self.feedback_timer > 0.0 and self.feedback_message:
            fb_surf = small_font.render(self.feedback_message, True, self.feedback_color)
            surface.blit(fb_surf, (screen_rect.centerx - fb_surf.get_width() // 2, screen_rect.centery - fb_surf.get_height() // 2))
        else:
            # Render digits with spacing
            disp_chars = []
            for i in range(self.code_length):
                if i < len(self.entered_digits):
                    disp_chars.append(self.entered_digits[i])
                elif i == len(self.entered_digits) and int(self.cursor_blink_timer) % 2 == 0:
                    disp_chars.append("_")
                else:
                    disp_chars.append("-")
            disp_text = "  ".join(disp_chars)
            disp_surf = lcd_font.render(disp_text, True, (80, 235, 100))
            surface.blit(disp_surf, (screen_rect.centerx - disp_surf.get_width() // 2, screen_rect.centery - disp_surf.get_height() // 2))

        # 4. 3x4 Button Grid
        btn_w = 46
        btn_h = 28
        gap_x = 10
        gap_y = 6
        grid_start_x = box_rect.centerx - (3 * btn_w + 2 * gap_x) // 2
        grid_start_y = screen_y + screen_h + 10

        for r in range(4):
            for c in range(3):
                bx = grid_start_x + c * (btn_w + gap_x)
                by = grid_start_y + r * (btn_h + gap_y)
                btn_rect = pygame.Rect(bx, by, btn_w, btn_h)

                is_selected = (r == self.selected_row and c == self.selected_col)
                val = self.grid[r][c]

                # Button colors
                if is_selected:
                    bg_col = (75, 70, 65)
                    border_col = (240, 200, 90)
                    text_col = (255, 245, 200)
                else:
                    bg_col = (38, 36, 40)
                    border_col = (60, 58, 64)
                    text_col = (190, 185, 180)

                if val == "C":
                    if is_selected:
                        bg_col = (90, 30, 30)
                    text_col = (230, 90, 90)
                elif val == "OK":
                    if is_selected:
                        bg_col = (30, 85, 40)
                    text_col = (90, 220, 110)

                pygame.draw.rect(surface, bg_col, btn_rect, border_radius=4)
                pygame.draw.rect(surface, border_col, btn_rect, width=2 if is_selected else 1, border_radius=4)

                btn_surf = small_font.render(val, True, text_col)
                surface.blit(btn_surf, (btn_rect.centerx - btn_surf.get_width() // 2, btn_rect.centery - btn_surf.get_height() // 2))

        # 5. Bottom Instructions Hint
        hint_surf = small_font.render(t("minigame_keypad_controls"), True, (160, 155, 140))
        surface.blit(hint_surf, (box_rect.centerx - hint_surf.get_width() // 2, box_rect.bottom - 16))
