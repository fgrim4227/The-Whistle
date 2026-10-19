"""
FuseBoxMinigame: Wiring circuit minigame in FirstRoom.
The player connects 4 colored wires across the fuse box terminals.
A mismatch triggers an electrical short-circuit that alerts El Silbón!
Connecting all wires restores electricity to the cabin, unlocking the final exit sensor.
"""

from typing import Any, Callable, Dict, Optional
import pygame

import settings
from src.i18n import t
from src.minigames.BaseMinigame import BaseMinigame


class FuseBoxMinigame(BaseMinigame):
    def __init__(
        self,
        play_state: Any,
        target_object: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(play_state, target_object, on_success, on_fail)

        self.wire_colors = [
            ("Rojo", (220, 50, 50)),
            ("Azul", (50, 110, 230)),
            ("Amarillo", (230, 200, 40)),
            ("Verde", (50, 190, 70)),
        ]

        # Left terminals in standard order (0..3)
        self.left_terminals = list(range(4))

        # Right terminals shuffled so they are not in 1:1 straight lines
        self.right_terminals = [1, 3, 0, 2]

        # Mapping of connected wires: left_idx -> right_idx
        self.connections: Dict[int, int] = {}

        self.selected_left: int = 0
        self.selected_right: int = 0
        self.is_selecting_right: bool = False

        self.spark_timer: float = 0.0
        self.feedback_message: str = ""
        self.feedback_color: tuple = (220, 220, 220)
        self.feedback_timer: float = 0.0

    def handle_input(self, event: pygame.event.Event) -> bool:
        if super().handle_input(event):
            return True

        if event.type == pygame.KEYDOWN:
            if not self.is_selecting_right:
                # Navigating left column
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.selected_left = (self.selected_left - 1) % 4
                    return True
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_left = (self.selected_left + 1) % 4
                    return True
                elif event.key in (pygame.K_d, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN):
                    # Enter right column selection
                    self.is_selecting_right = True
                    self.selected_right = self.selected_left
                    return True
                # Direct number shortcut 1-4 to connect selected left to right slot
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    r_idx = event.key - pygame.K_1
                    self._attempt_connection(self.selected_left, r_idx)
                    return True
            else:
                # Navigating right column
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.selected_right = (self.selected_right - 1) % 4
                    return True
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_right = (self.selected_right + 1) % 4
                    return True
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    self.is_selecting_right = False
                    return True
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._attempt_connection(self.selected_left, self.selected_right)
                    self.is_selecting_right = False
                    return True

        return False

    def handle_action(self, input_id: str, input_data: Any) -> bool:
        if super().handle_action(input_id, input_data):
            return True

        if getattr(input_data, "pressed", True):
            if not self.is_selecting_right:
                if input_id == "move_up":
                    self.selected_left = (self.selected_left - 1) % 4
                    return True
                elif input_id == "move_down":
                    self.selected_left = (self.selected_left + 1) % 4
                    return True
                elif input_id in ("move_right", "action", "enter", "interact"):
                    self.is_selecting_right = True
                    self.selected_right = self.selected_left
                    return True
                elif input_id.startswith("slot_"):
                    try:
                        slot_num = int(input_id.split("_")[1]) - 1
                        if 0 <= slot_num < 4:
                            self._attempt_connection(self.selected_left, slot_num)
                            return True
                    except Exception:
                        pass
            else:
                if input_id == "move_up":
                    self.selected_right = (self.selected_right - 1) % 4
                    return True
                elif input_id == "move_down":
                    self.selected_right = (self.selected_right + 1) % 4
                    return True
                elif input_id == "move_left":
                    self.is_selecting_right = False
                    return True
                elif input_id in ("action", "enter", "interact"):
                    self._attempt_connection(self.selected_left, self.selected_right)
                    self.is_selecting_right = False
                    return True
        return False

    def _attempt_connection(self, left_idx: int, right_idx: int) -> None:
        left_color_id = left_idx
        target_right_color_id = self.right_terminals[right_idx]

        if left_color_id == target_right_color_id:
            # Correct connection!
            self.connections[left_idx] = right_idx
            settings.play_sound("minigame_unlock_click", loops=0, volume=0.9, channel_name="minigame")
            self.feedback_message = t("minigame_fuse_connected")
            self.feedback_color = (60, 230, 60)
            self.feedback_timer = 1.5

            # Auto advance to next unconnected left wire
            unconnected = [i for i in range(4) if i not in self.connections]
            if unconnected:
                self.selected_left = unconnected[0]
            else:
                # All 4 connected!
                self.is_completed = True
                settings.play_sound("minigame_unlock_click", loops=0, volume=1.0, channel_name="minigame")
                if hasattr(self.play_state, "house"):
                    setattr(self.play_state.house, "power_restored", True)
                if hasattr(self.play_state, "player"):
                    self.play_state.player.set_thought("thought_fuse_box", 4.5)

                if self.on_success:
                    self.on_success()
                self.close()
        else:
            # Electrical short-circuit failure!
            self.spark_timer = 0.4
            self.feedback_message = t("minigame_fuse_shortcircuit")
            self.feedback_color = (255, 60, 60)
            self.feedback_timer = 2.5
            self.alert_monster(radius=1000, sound_name="minigame_lock_forced", volume=1.0)
            if self.on_fail:
                self.on_fail()

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.feedback_timer > 0.0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)
        if self.spark_timer > 0.0:
            self.spark_timer = max(0.0, self.spark_timer - dt)

    def render(self, surface: pygame.Surface) -> None:
        # 1. Dark semi-transparent backdrop
        backdrop = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        backdrop.fill((8, 10, 14, 175))
        surface.blit(backdrop, (0, 0))

        center_x = settings.VIRTUAL_WIDTH // 2
        center_y = settings.VIRTUAL_HEIGHT // 2 + 6

        # 2. Outer Metal Box
        panel_w, panel_h = 240, 160
        panel_rect = pygame.Rect(center_x - panel_w // 2, center_y - panel_h // 2, panel_w, panel_h)
        pygame.draw.rect(surface, (28, 32, 36), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 70, 80), panel_rect, width=2, border_radius=8)

        # Header Title & Main Power Indicator
        title_font = settings.FONTS.get("medium", settings.FONTS["small"])
        title_surf = title_font.render(t("minigame_fuse_title"), True, (200, 220, 240))
        surface.blit(title_surf, (center_x - title_surf.get_width() // 2, panel_rect.top + 8))

        # Power Status LED in top right corner
        power_color = (60, 230, 60) if len(self.connections) == 4 else (220, 40, 40)
        pygame.draw.circle(surface, power_color, (panel_rect.right - 18, panel_rect.top + 16), 6)
        pygame.draw.circle(surface, (160, 160, 160), (panel_rect.right - 18, panel_rect.top + 16), 6, width=1)

        # 3. Terminals Layout
        left_col_x = panel_rect.left + 35
        right_col_x = panel_rect.right - 35
        start_y = panel_rect.top + 40
        row_spacing = 24

        left_pos = []
        right_pos = []
        for i in range(4):
            ly = start_y + i * row_spacing
            left_pos.append((left_col_x, ly))
            right_pos.append((right_col_x, ly))

        # Draw already connected wires
        for l_idx, r_idx in self.connections.items():
            color = self.wire_colors[l_idx][1]
            p1 = left_pos[l_idx]
            p2 = right_pos[r_idx]
            pygame.draw.line(surface, color, p1, p2, 4)
            pygame.draw.line(surface, (255, 255, 255), p1, p2, 1)

        # Draw currently dragged wire if selecting right
        if self.is_selecting_right and self.selected_left not in self.connections:
            color = self.wire_colors[self.selected_left][1]
            p1 = left_pos[self.selected_left]
            p2 = right_pos[self.selected_right]
            pygame.draw.line(surface, color, p1, p2, 3)

        # Draw Left Terminals
        small_font = settings.FONTS.get("small", settings.FONTS["small"])
        for i in range(4):
            pos = left_pos[i]
            color = self.wire_colors[i][1]
            is_selected = (self.selected_left == i and not self.is_selecting_right)
            # Terminal socket
            pygame.draw.circle(surface, (15, 15, 18), pos, 9)
            pygame.draw.circle(surface, color, pos, 6)
            if is_selected:
                pygame.draw.circle(surface, (255, 255, 255), pos, 10, width=2)

            # Left Label
            lbl = small_font.render(str(i + 1), True, (180, 180, 190))
            surface.blit(lbl, (pos[0] - 18, pos[1] - lbl.get_height() // 2))

        # Draw Right Terminals
        for i in range(4):
            pos = right_pos[i]
            target_color_id = self.right_terminals[i]
            color = self.wire_colors[target_color_id][1]
            is_selected = (self.is_selecting_right and self.selected_right == i)
            # Terminal socket
            pygame.draw.circle(surface, (15, 15, 18), pos, 9)
            pygame.draw.circle(surface, color, pos, 6)
            if is_selected:
                pygame.draw.circle(surface, (255, 255, 255), pos, 10, width=2)

            # Right Label
            lbl = small_font.render(str(i + 1), True, (180, 180, 190))
            surface.blit(lbl, (pos[0] + 12, pos[1] - lbl.get_height() // 2))

        # 4. Short-circuit Spark Effect
        if self.spark_timer > 0.0:
            spark_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            spark_surf.fill((255, 255, 255, int(150 * (self.spark_timer / 0.4))))
            surface.blit(spark_surf, panel_rect.topleft)

        # 5. Feedback or Hint
        if self.feedback_timer > 0.0 and self.feedback_message:
            fb_surf = small_font.render(self.feedback_message, True, self.feedback_color)
            surface.blit(fb_surf, (center_x - fb_surf.get_width() // 2, panel_rect.bottom - 28))
        else:
            hint_surf = small_font.render(t("minigame_fuse_hint"), True, (160, 175, 190))
            surface.blit(hint_surf, (center_x - hint_surf.get_width() // 2, panel_rect.bottom - 28))

        # Controls Hint
        ctrl_surf = small_font.render(t("minigame_fuse_controls"), True, (190, 200, 210))
        surface.blit(ctrl_surf, (center_x - ctrl_surf.get_width() // 2, panel_rect.bottom - 14))
