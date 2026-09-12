"""
Player class (Paramedic protagonist - Andreas).
Manages directional movement with collisions, spritesheet animations,
flashlight, battery consumption, stealth hiding state, and inner monologues.
"""

from typing import Optional, List, Dict, Tuple
import pygame
from gale.animation import Animation
from gale import frames

import settings
from src.entities.BaseEntity import BaseEntity
from src.i18n import t


class Player(BaseEntity):
    def __init__(self, x: float, y: float) -> None:
        # Andreas sprite dimensions: 16x32 px
        super().__init__(x, y, width=16, height=32, speed=settings.PLAYER_SPEED)
        self.flashlight_on = True
        self.battery = 100.0
        self.is_hidden = False
        self.current_hiding_spot = None
        self.equipped_item: Optional[str] = None
        self.panic_meter = 0.0
        
        # Directional animations
        self.animations: Dict[str, Animation] = self._create_animations()
        self.current_animation = self.animations.get("idle-down")
        self.is_moving = False

        # Internal thought / monologue system
        self.current_thought: Optional[str] = "thought_intro"
        self.thought_timer = 5.0

    def _create_animations(self) -> Dict[str, Animation]:
        anims = {}
        tex = settings.TEXTURES

        def slice_sheet(key: str, fw: int, fh: int) -> List[pygame.Surface]:
            img = tex.get(key)
            if img:
                rects = frames.generate_frames(img, fw, fh)
                return [img.subsurface(r) for r in rects]
            # Geometric fallback if texture is unavailable
            dummy = pygame.Surface((fw, fh), pygame.SRCALPHA)
            pygame.draw.rect(dummy, (40, 90, 160), (0, 0, fw, fh))
            return [dummy]

        anims["walk-down"] = Animation(slice_sheet("player_walk_down", 16, 32), 0.12)
        anims["walk-up"] = Animation(slice_sheet("player_walk_up", 16, 32), 0.12)
        anims["walk-left"] = Animation(slice_sheet("player_walk_left", 16, 32), 0.12)
        anims["walk-right"] = Animation(slice_sheet("player_walk_right", 16, 32), 0.12)

        idle_frames = slice_sheet("player_idle", 16, 32)
        anims["idle-down"] = Animation(idle_frames, 0.25)
        anims["idle-up"] = Animation(idle_frames, 0.25)
        anims["idle-left"] = Animation(idle_frames, 0.25)
        anims["idle-right"] = Animation(idle_frames, 0.25)

        anims["dying"] = Animation(slice_sheet("player_dying", 16, 32), 0.18, loops=1)
        return anims

    def change_animation(self, anim_name: str) -> None:
        if anim_name in self.animations and self.current_animation != self.animations[anim_name]:
            self.current_animation = self.animations[anim_name]
            self.current_animation.reset()

    def get_collision_rect(self) -> pygame.Rect:
        # Feet collision rect (bottom 16x16 area) for natural top-down perspective
        return pygame.Rect(int(self.x), int(self.y + 16), 16, 16)

    def toggle_flashlight(self) -> None:
        if self.battery > 0:
            self.flashlight_on = not self.flashlight_on
        else:
            self.flashlight_on = False

    def recharge_battery(self, amount: float = settings.BATTERY_RECHARGE_AMOUNT) -> None:
        self.battery = min(100.0, self.battery + amount)
        self.flashlight_on = True

    def set_thought(self, text_key: str, duration: float = 4.0) -> None:
        self.current_thought = text_key
        self.thought_timer = duration

    def hide(self, spot) -> None:
        self.is_hidden = True
        self.current_hiding_spot = spot
        self.flashlight_on = False
        self.vx = 0.0
        self.vy = 0.0

    def exit_hide(self) -> None:
        self.is_hidden = False
        self.current_hiding_spot = None

    def update_movement_from_input(self, pressed_keys: dict, obstacles: List[pygame.Rect], dt: float) -> None:
        if self.is_hidden:
            return

        dx = 0.0
        dy = 0.0

        if pressed_keys.get("move_left", False):
            dx -= 1.0
            self.direction = "left"
        if pressed_keys.get("move_right", False):
            dx += 1.0
            self.direction = "right"
        if pressed_keys.get("move_up", False):
            dy -= 1.0
            self.direction = "up"
        if pressed_keys.get("move_down", False):
            dy += 1.0
            self.direction = "down"

        self.is_moving = (dx != 0.0 or dy != 0.0)

        # Select matching animation
        if self.is_moving:
            self.change_animation(f"walk-{self.direction}")
            # Normalize diagonal movement
            if dx != 0.0 and dy != 0.0:
                inv = 0.70710678
                dx *= inv
                dy *= inv
        else:
            self.change_animation(f"idle-{self.direction}")

        # Collision resolution per axis on character feet
        new_x = self.x + dx * self.speed * dt
        feet_rect_x = pygame.Rect(int(new_x), int(self.y + 16), 16, 16)
        if not any(feet_rect_x.colliderect(obs) for obs in obstacles):
            self.x = new_x

        new_y = self.y + dy * self.speed * dt
        feet_rect_y = pygame.Rect(int(self.x), int(new_y + 16), 16, 16)
        if not any(feet_rect_y.colliderect(obs) for obs in obstacles):
            self.y = new_y

    def update(self, dt: float) -> None:
        # Update active animation frame
        if self.current_animation:
            self.current_animation.update(dt)

        # Flashlight battery drain
        if self.flashlight_on:
            self.battery = max(0.0, self.battery - settings.BATTERY_DRAIN_RATE * dt)
            if self.battery <= 0.0:
                self.flashlight_on = False

        # Thought display timer
        if self.thought_timer > 0.0:
            self.thought_timer -= dt
            if self.thought_timer <= 0.0:
                self.current_thought = None

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        if self.is_hidden:
            return  # Hidden inside wardrobe/table

        ox, oy = camera_offset
        draw_x = int(self.x - ox)
        draw_y = int(self.y - oy)

        # 1. Draw Andreas current animation frame
        if self.current_animation:
            frame = self.current_animation.get_current_frame()
            if isinstance(frame, pygame.Surface):
                surface.blit(frame, (draw_x, draw_y))
            else:
                pygame.draw.rect(surface, (40, 90, 160), self.get_rect().move(-ox, -oy))
        else:
            pygame.draw.rect(surface, (40, 90, 160), self.get_rect().move(-ox, -oy))

        # 2. Flashlight origin indicator light if active
        if self.flashlight_on and self.battery > 0:
            beam_offsets = {
                "down": (draw_x + 8, draw_y + 20),
                "up": (draw_x + 8, draw_y + 10),
                "left": (draw_x + 2, draw_y + 18),
                "right": (draw_x + 14, draw_y + 18),
            }
            bx, by = beam_offsets.get(self.direction, (draw_x + 8, draw_y + 20))
            pygame.draw.circle(surface, (255, 250, 200), (int(bx), int(by)), 2)

        # 3. Inner monologue banner
        if self.current_thought:
            thought_text = t(self.current_thought)
            txt_surf = settings.FONTS["small"].render(f'"{thought_text}"', True, (240, 240, 240))
            bg_rect = txt_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 35))
            pygame.draw.rect(surface, (0, 0, 0, 160), bg_rect.inflate(12, 6), border_radius=4)
            surface.blit(txt_surf, bg_rect)
