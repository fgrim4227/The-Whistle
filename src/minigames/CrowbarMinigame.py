"""
CrowbarMinigame: Button-mashing resistance minigame to pry wooden planks off barricaded doors.
The player mashes SPACE/E against decaying tension. When the plank snaps (wood_break.mp3),
it emits a deafening crack that immediately alerts El Silbón to investigate!
"""

import math
from typing import Any, Callable, Optional
import pygame

import settings
from src.i18n import t
from src.minigames.BaseMinigame import BaseMinigame


class CrowbarMinigame(BaseMinigame):
    def __init__(
        self,
        play_state: Any,
        target_door: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
        target_object: Any = None,
    ) -> None:
        target = target_door if target_door is not None else target_object
        super().__init__(play_state, target, on_success, on_fail)

        self.progress: float = 0.0  # 0 to 100
        self.decay_rate: float = 24.0  # Resistance pushing back per second
        self.mash_gain: float = 12.0  # Progress gained per keypress

        # Planks tracking on the target door
        if hasattr(self.target_object, "planks_remaining"):
            self.total_planks = getattr(self.target_object, "planks_remaining", 3)
        else:
            self.total_planks = 3

        self.just_snapped: bool = False
        self.snap_timer: float = 0.0

    def handle_input(self, event: pygame.event.Event) -> bool:
        if super().handle_input(event):
            return True

        if not self.just_snapped and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
                self._apply_mash()
                return True
        return False

    def handle_action(self, input_id: str, input_data: Any) -> bool:
        if super().handle_action(input_id, input_data):
            return True

        if not self.just_snapped and getattr(input_data, "pressed", True):
            if input_id in ("action", "interact", "enter"):
                self._apply_mash()
                return True
        return False

    def _apply_mash(self) -> None:
        if self.just_snapped:
            return
        self.progress = min(100.0, self.progress + self.mash_gain)
        # Subtle creak sound on strong leverage
        if self.progress > 60.0 and int(self.progress) % 24 < 12:
            settings.play_sound("minigame_normal_click", loops=0, volume=0.3, channel_name="minigame")

        if self.progress >= 100.0:
            self._trigger_snap()

    def _trigger_snap(self) -> None:
        if self.just_snapped:
            return
        self.just_snapped = True
        self.snap_timer = 0.0

        # Loud wood breaking sound + alert El Silbón
        self.alert_monster(radius=2000, sound_name="minigame_wood_break", volume=1.0)

        # Deduct a plank from target door
        if hasattr(self.target_object, "planks_remaining"):
            self.target_object.planks_remaining = max(0, self.target_object.planks_remaining - 1)
            if self.target_object.planks_remaining == 0:
                self.target_object.unbar()
                self.is_completed = True

        if hasattr(self.play_state, "player"):
            self.play_state.player.set_thought("thought_door_unbarred", 4.0)

        if self.on_success:
            self.on_success()

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.is_active:
            return

        if self.just_snapped:
            self.snap_timer += dt
            if self.snap_timer > 0.8:
                # Close minigame after showing splinter break effect
                self.close()
            return

        if self.progress >= 100.0:
            self._trigger_snap()
        else:
            # Continuous resistance decay pushing back
            self.progress = max(0.0, self.progress - self.decay_rate * dt)

    def render(self, surface: pygame.Surface) -> None:
        # 1. Dark semi-transparent backdrop
        backdrop = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        backdrop.fill((10, 8, 6, 175))
        surface.blit(backdrop, (0, 0))

        center_x = settings.VIRTUAL_WIDTH // 2
        center_y = settings.VIRTUAL_HEIGHT // 2 + 6

        # 2. Main Frame
        panel_w, panel_h = 240, 160
        panel_rect = pygame.Rect(center_x - panel_w // 2, center_y - panel_h // 2, panel_w, panel_h)
        pygame.draw.rect(surface, (38, 28, 20), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (80, 55, 35), panel_rect, width=2, border_radius=8)

        # Header Title
        title_font = settings.FONTS.get("medium", settings.FONTS["small"])
        title_surf = title_font.render(t("minigame_crowbar_title"), True, (245, 220, 160))
        surface.blit(title_surf, (center_x - title_surf.get_width() // 2, panel_rect.top + 8))

        # Remaining Planks Indicator
        planks_left = getattr(self.target_object, "planks_remaining", 1) if self.target_object else 1
        small_font = settings.FONTS.get("small", settings.FONTS["small"])
        plank_info_surf = small_font.render(t("minigame_crowbar_planks_left", count=planks_left), True, (200, 180, 150))
        surface.blit(plank_info_surf, (center_x - plank_info_surf.get_width() // 2, panel_rect.top + 28))

        # 3. Wooden Plank & Crowbar Illustration
        wood_y = center_y - 8
        wood_rect = pygame.Rect(center_x - 80, wood_y, 160, 24)

        if self.just_snapped:
            # Splintered broken plank halves
            left_half = pygame.Rect(wood_rect.left, wood_y - 6, 70, 24)
            right_half = pygame.Rect(wood_rect.right - 70, wood_y + 8, 70, 24)
            pygame.draw.rect(surface, (140, 95, 55), left_half, border_radius=3)
            pygame.draw.rect(surface, (140, 95, 55), right_half, border_radius=3)
            # Break notice
            break_font = settings.FONTS.get("dialogue", settings.FONTS["small"])
            break_surf = break_font.render(t("minigame_crowbar_break"), True, (255, 60, 60))
            surface.blit(break_surf, (center_x - break_surf.get_width() // 2, wood_y + 36))
        else:
            # Solid plank under strain
            pygame.draw.rect(surface, (130, 90, 50), wood_rect, border_radius=3)
            pygame.draw.rect(surface, (80, 50, 25), wood_rect, width=2, border_radius=3)
            # Nails at ends
            pygame.draw.circle(surface, (70, 70, 75), (wood_rect.left + 10, wood_rect.centery), 3)
            pygame.draw.circle(surface, (70, 70, 75), (wood_rect.right - 10, wood_rect.centery), 3)

            # Red Crowbar hooking under the plank (flexing with progress)
            leverage_angle = -20.0 + (self.progress / 100.0) * 35.0
            rad = math.radians(leverage_angle)
            bar_start = (wood_rect.centerx - 15, wood_rect.top + 4)
            bar_len = 50
            bar_end = (bar_start[0] + bar_len * math.cos(rad), bar_start[1] - bar_len * math.sin(rad))
            pygame.draw.line(surface, (180, 40, 40), bar_start, bar_end, 5)
            # Crowbar curved hook
            pygame.draw.circle(surface, (180, 40, 40), bar_start, 4)

            # 4. Progress / Force Meter Bar
            meter_w, meter_h = 160, 14
            meter_x = center_x - meter_w // 2
            meter_y = wood_y + 36
            pygame.draw.rect(surface, (20, 16, 14), (meter_x, meter_y, meter_w, meter_h), border_radius=4)

            fill_w = int((self.progress / 100.0) * meter_w)
            if fill_w > 0:
                # Color gradient from yellow to bright green/red
                bar_color = (
                    int(255 * min(1.0, 2.0 * (1.0 - self.progress / 100.0))),
                    int(255 * min(1.0, 2.0 * (self.progress / 100.0))),
                    50,
                )
                pygame.draw.rect(surface, bar_color, (meter_x, meter_y, fill_w, meter_h), border_radius=4)
            pygame.draw.rect(surface, (100, 90, 80), (meter_x, meter_y, meter_w, meter_h), width=1, border_radius=4)

            # Mash Action Callout
            action_text = t("minigame_crowbar_action")
            action_surf = small_font.render(action_text, True, (255, 230, 80))
            surface.blit(action_surf, (center_x - action_surf.get_width() // 2, meter_y + 18))

        # Bottom Controls Hint
        ctrl_surf = small_font.render(t("minigame_crowbar_controls"), True, (210, 200, 170))
        surface.blit(ctrl_surf, (center_x - ctrl_surf.get_width() // 2, panel_rect.bottom - 16))
