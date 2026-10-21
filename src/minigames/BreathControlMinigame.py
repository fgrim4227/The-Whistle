"""Horizontal breath-control minigame played while Andreas is hiding."""

import random
from typing import Any, Callable, Optional

import pygame

import settings
from src.i18n import t
from src.minigames.BaseMinigame import BaseMinigame


class BreathControlMinigame(BaseMinigame):
    TRACK_WIDTH = 320
    SAFE_WIDTH = 61.6
    BALL_RADIUS = 6
    PANIC_LIMIT = 1.8
    PANIC_RECOVERY_RATE = 1.25
    SAFE_ZONE_SPEED = 190.0

    def __init__(
        self,
        play_state: Any,
        target_object: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(play_state, target_object, on_success, on_fail)
        self.space_held = False
        self.track_left = (settings.VIRTUAL_WIDTH - self.TRACK_WIDTH) / 2
        self.track_right = self.track_left + self.TRACK_WIDTH
        self.safe_center = settings.VIRTUAL_WIDTH / 2
        self.ball_x = self.safe_center
        self.ball_velocity = random.choice((-1.0, 1.0)) * random.uniform(65.0, 105.0)
        self.direction_change_timer = random.uniform(0.65, 1.25)
        self.panic = 0.0

    def handle_action(self, input_id: str, input_data: Any) -> bool:
        if super().handle_action(input_id, input_data):
            if self.play_state.player.is_hidden:
                self.play_state.player.exit_hide()
            return True

        if input_id == "action":
            self.space_held = bool(getattr(input_data, "pressed", True))
            return True

        if input_id == "interact" and getattr(input_data, "pressed", True):
            self._leave_hiding()
            return True

        return False

    def _leave_hiding(self) -> None:
        self.close()
        if self.play_state.player.is_hidden:
            self.play_state.player.exit_hide()

    def _fail(self) -> None:
        player = self.play_state.player
        monster = self.play_state.monster
        player_x, player_y = player.get_center()

        monster.hear_noise(player_x, player_y, radius=1000.0)
        self.play_state.hide_cooldown = settings.HIDE_RETRY_COOLDOWN
        settings.stop_channel("player_hidden_breath")
        self.close()
        player.exit_hide()
        player.set_thought("thought_breathing_failed", duration=3.0)

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.is_active:
            return

        if not self.play_state.player.is_hidden:
            self.close()
            return

        movement = 1.0 if self.space_held else -1.0
        half_safe_width = self.SAFE_WIDTH / 2
        self.safe_center += movement * self.SAFE_ZONE_SPEED * dt
        self.safe_center = max(
            self.track_left + half_safe_width,
            min(self.track_right - half_safe_width, self.safe_center),
        )

        self.direction_change_timer -= dt
        if self.direction_change_timer <= 0.0:
            self.ball_velocity = random.choice((-1.0, 1.0)) * random.uniform(65.0, 115.0)
            self.direction_change_timer = random.uniform(0.55, 1.25)

        self.ball_x += self.ball_velocity * dt
        ball_min = self.track_left + self.BALL_RADIUS
        ball_max = self.track_right - self.BALL_RADIUS
        if self.ball_x <= ball_min:
            self.ball_x = ball_min
            self.ball_velocity = abs(self.ball_velocity)
        elif self.ball_x >= ball_max:
            self.ball_x = ball_max
            self.ball_velocity = -abs(self.ball_velocity)

        safe_left = self.safe_center - half_safe_width
        safe_right = self.safe_center + half_safe_width
        if safe_left <= self.ball_x <= safe_right:
            self.panic = max(0.0, self.panic - self.PANIC_RECOVERY_RATE * dt)
        else:
            self.panic += dt
            if self.panic >= self.PANIC_LIMIT:
                self._fail()

    def render(self, surface: pygame.Surface) -> None:
        panel_rect = pygame.Rect(58, 224, settings.VIRTUAL_WIDTH - 116, 60)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel.fill((10, 9, 13, 238))
        surface.blit(panel, panel_rect.topleft)
        pygame.draw.rect(surface, (115, 93, 81), panel_rect, width=1, border_radius=5)

        center_x = settings.VIRTUAL_WIDTH // 2
        instruction = settings.FONTS["hud"].render(t("breathing_instruction"), True, (235, 225, 210))
        surface.blit(instruction, instruction.get_rect(center=(center_x, 232)))

        track_rect = pygame.Rect(int(self.track_left), 243, self.TRACK_WIDTH, 18)
        pygame.draw.rect(surface, (30, 29, 34), track_rect, border_radius=4)
        pygame.draw.rect(surface, (120, 115, 110), track_rect, width=1, border_radius=4)

        safe_rect = pygame.Rect(
            round(self.safe_center - self.SAFE_WIDTH / 2),
            track_rect.top + 2,
            round(self.SAFE_WIDTH),
            track_rect.height - 4,
        )
        pygame.draw.rect(surface, (80, 145, 105), safe_rect, border_radius=3)
        pygame.draw.circle(
            surface,
            (220, 35, 42),
            (round(self.ball_x), track_rect.centery),
            self.BALL_RADIUS,
        )
        pygame.draw.circle(
            surface,
            (255, 145, 145),
            (round(self.ball_x - 2), track_rect.centery - 2),
            2,
        )

        panic_rect = pygame.Rect(track_rect.left, 266, self.TRACK_WIDTH, 5)
        pygame.draw.rect(surface, (45, 35, 36), panic_rect, border_radius=2)
        panic_fill = panic_rect.copy()
        panic_fill.width = round(panic_rect.width * min(1.0, self.panic / self.PANIC_LIMIT))
        if panic_fill.width:
            pygame.draw.rect(surface, (190, 45, 45), panic_fill, border_radius=2)
