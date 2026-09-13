"""
HUD module for rendering flashlight battery gauge, equipped item, prompts, and stealth indicators.
"""

import math
import pygame

import settings
from src.i18n import t


class HUD:
    def __init__(self) -> None:
        self.pulse_timer = 0.0

    def update(self, dt: float) -> None:
        self.pulse_timer += dt

    def render(self, surface: pygame.Surface, player, audio_manager, prompt_text: str = "") -> None:
        # 1. Flashlight Battery Gauge (Top-Left)
        bat_w = 60
        bat_h = 10
        bat_x = 12
        bat_y = 12

        # Battery outline
        pygame.draw.rect(surface, (40, 40, 40), (bat_x, bat_y, bat_w, bat_h), border_radius=2)
        pygame.draw.rect(surface, (200, 200, 200), (bat_x, bat_y, bat_w, bat_h), width=1, border_radius=2)
        pygame.draw.rect(surface, (200, 200, 200), (bat_x + bat_w, bat_y + 2, 3, bat_h - 4))

        # Battery charge fill
        pct = max(0.0, player.battery / 100.0)
        fill_w = int((bat_w - 4) * pct)
        if pct > 0.5:
            fill_col = (50, 210, 50)
        elif pct > 0.2:
            fill_col = (230, 190, 30)
        else:
            # Flashing red when battery is low
            blink = int(150 + 100 * math.sin(self.pulse_timer * 8.0))
            fill_col = (blink, 20, 20)

        if fill_w > 0:
            pygame.draw.rect(surface, fill_col, (bat_x + 2, bat_y + 2, fill_w, bat_h - 4))

        bat_label = settings.FONTS["small"].render(f"{t('hud_battery')}: {int(player.battery)}%", True, settings.COLOR_WHITE)
        surface.blit(bat_label, (bat_x + bat_w + 8, bat_y - 1))

        # 2. Multi-slot inventory indicator (Top-Right)
        if hasattr(player, "inventory") and player.inventory:
            inv_surfs = []
            for idx, it in enumerate(player.inventory):
                is_selected = (idx == player.selected_item_index)
                name = t(f"item_{it}")
                label = f"[{idx + 1}:{name}]" if not is_selected else f"> {idx + 1}:{name} <"
                color = settings.COLOR_GOLD if is_selected else (170, 165, 150)
                inv_surfs.append(settings.FONTS["small"].render(label, True, color))

            cur_x = settings.VIRTUAL_WIDTH - 12
            for s in reversed(inv_surfs):
                cur_x -= s.get_width()
                surface.blit(s, (cur_x, 12))
                cur_x -= 8
        else:
            item_name = t(f"item_{player.equipped_item}") if player.equipped_item else t("hud_none")
            item_text = f"{t('hud_equipped')}: {item_name}"
            item_surf = settings.FONTS["small"].render(item_text, True, settings.COLOR_GOLD)
            surface.blit(item_surf, (settings.VIRTUAL_WIDTH - item_surf.get_width() - 12, 12))

        # 3. Concealment status indicator (Wardrobe / Table)
        if player.is_hidden:
            hidden_surf = settings.FONTS["small"].render(t("hud_hidden"), True, (100, 220, 100))
            surface.blit(hidden_surf, (settings.VIRTUAL_WIDTH // 2 - hidden_surf.get_width() // 2, 12))

        # 4. Terror warning when El Silbón is stalking close
        if audio_manager.is_near_alert and not player.is_hidden:
            pulse = int(180 + 75 * math.sin(self.pulse_timer * 12.0))
            alert_surf = settings.FONTS["small"].render(t("hud_silbon_near"), True, (pulse, 30, 30))
            surface.blit(alert_surf, (settings.VIRTUAL_WIDTH // 2 - alert_surf.get_width() // 2, 28))

        # 5. Contextual interaction prompt at bottom center
        if prompt_text:
            p_surf = settings.FONTS["small"].render(prompt_text, True, settings.COLOR_WHITE)
            bg_rect = p_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 16))
            pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect.inflate(10, 4), border_radius=3)
            surface.blit(p_surf, bg_rect)

        # 6. Character thoughts & NPC dialogue banner (rendered on top of lighting)
        player.render_thought(surface, prompt_active=bool(prompt_text))

