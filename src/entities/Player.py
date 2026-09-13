"""
Player class (Paramedic protagonist - Andreas).
Manages directional movement with collisions, spritesheet animations,
flashlight, battery consumption, stealth hiding state, and inner monologues.
"""

from typing import Optional, List, Dict, Tuple
import pygame
from gale.animation import Animation
from gale.state import StateMachine

import settings
from src.definitions import entity as entity_defs
from src.entities.BaseEntity import BaseEntity
from src.i18n import t
from src.states.entity.PlayerHidingState import PlayerHidingState
from src.states.entity.PlayerIdleState import PlayerIdleState
from src.states.entity.PlayerWalkState import PlayerWalkState


class Player(BaseEntity):
    def __init__(self, x: float, y: float) -> None:
        width, height = entity_defs.PLAYER_SIZE
        super().__init__(x, y, width=width, height=height, speed=settings.PLAYER_SPEED)
        self.flashlight_on = True
        self.battery = 100.0
        self.is_hidden = False
        self.current_hiding_spot = None
        
        # Multi-slot inventory system (stores collected tools & keys)
        self.inventory: List[str] = []
        self.selected_item_index: int = 0

        self.panic_meter = 0.0
        
        # Directional animations
        self.animations: Dict[str, Animation]
        self._animation_textures: Dict[str, str]
        self.animations, self._animation_textures = self._create_animations()
        self.current_animation = self.animations.get("idle-down")
        self.current_texture = self._animation_textures.get("idle-down")
        self.is_moving = False

        self.state_machine = StateMachine({
            "idle": lambda sm: PlayerIdleState(self, sm),
            "walk": lambda sm: PlayerWalkState(self, sm),
            "hiding": lambda sm: PlayerHidingState(self, sm),
        })
        self.state_name = "idle"
        self.state_machine.change(self.state_name)

        # Internal thought / monologue system
        self.current_thought: Optional[str] = "thought_intro"
        self.thought_timer = 5.0

    @property
    def equipped_item(self) -> Optional[str]:
        """Returns the currently selected item in the inventory, if any."""
        if 0 <= self.selected_item_index < len(self.inventory):
            return self.inventory[self.selected_item_index]
        return None

    @equipped_item.setter
    def equipped_item(self, item: Optional[str]) -> None:
        if item is None:
            return
        if item not in self.inventory:
            if len(self.inventory) < 5:
                self.inventory.append(item)
                self.selected_item_index = len(self.inventory) - 1
            else:
                self.inventory[self.selected_item_index] = item
        else:
            self.selected_item_index = self.inventory.index(item)

    def add_item(self, item: str) -> bool:
        """Adds an item to inventory without overwriting existing items."""
        if item not in self.inventory:
            if len(self.inventory) < 5:
                self.inventory.append(item)
                self.selected_item_index = len(self.inventory) - 1
                return True
            return False
        self.selected_item_index = self.inventory.index(item)
        return True

    def remove_item(self, item: str) -> bool:
        """Removes an item from inventory (e.g. consumed keys)."""
        if item in self.inventory:
            self.inventory.remove(item)
            if self.selected_item_index >= len(self.inventory):
                self.selected_item_index = max(0, len(self.inventory) - 1)
            return True
        return False

    def has_item(self, item: Optional[str]) -> bool:
        """Checks if player possesses the given item in any inventory slot."""
        if not item:
            return False
        return item in self.inventory

    def select_slot(self, index: int) -> None:
        """Selects an active inventory slot by index (0-4)."""
        if 0 <= index < len(self.inventory):
            self.selected_item_index = index

    def cycle_item(self) -> None:
        """Cycles to the next item in inventory."""
        if self.inventory:
            self.selected_item_index = (self.selected_item_index + 1) % len(self.inventory)

    def _create_animations(self) -> Tuple[Dict[str, Animation], Dict[str, str]]:
        return entity_defs.build_animations(
            entity_defs.PLAYER_ANIMATIONS, entity_defs.PLAYER_FALLBACK_COLOR, entity_defs.PLAYER_SIZE
        )

    def change_animation(self, anim_name: str) -> None:
        if anim_name in self.animations and self.current_animation != self.animations[anim_name]:
            self.current_animation = self.animations[anim_name]
            self.current_animation.reset()
            self.current_texture = self._animation_textures.get(anim_name)

    def change_state(self, state_name: str, *args, **kwargs) -> None:
        if state_name == self.state_name:
            return
        self.state_machine.change(state_name, *args, **kwargs)
        self.state_name = state_name

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
        self.change_state("hiding")

    def exit_hide(self) -> None:
        self.is_hidden = False
        self.current_hiding_spot = None
        self.change_state("idle")

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
        self.change_state("walk" if self.is_moving else "idle")

        if dx != 0.0 and dy != 0.0:
            inv = 0.70710678
            dx *= inv
            dy *= inv

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
            if isinstance(frame, pygame.Rect):
                surface.blit(settings.TEXTURES[self.current_texture], (draw_x, draw_y), frame)
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (draw_x, draw_y))
            else:
                pygame.draw.rect(surface, entity_defs.PLAYER_FALLBACK_COLOR, self.get_rect().move(-ox, -oy))
        else:
            pygame.draw.rect(surface, entity_defs.PLAYER_FALLBACK_COLOR, self.get_rect().move(-ox, -oy))

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

    def render_thought(self, surface: pygame.Surface, prompt_active: bool = False) -> None:
        """Renders character thoughts and dialogue banners in screen space on top of lighting."""
        if not self.current_thought:
            return

        thought_text = t(self.current_thought)
        font = settings.FONTS["small"]
        max_w = settings.VIRTUAL_WIDTH - 48

        # Word wrap into lines if text exceeds canvas width
        words = f'"{thought_text}"'.split(" ")
        lines = []
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            if font.size(test_line)[0] <= max_w:
                cur_line.append(word)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))

        if not lines:
            return

        rendered_lines = [font.render(l, True, (245, 245, 245)) for l in lines]
        total_h = sum(r.get_height() for r in rendered_lines) + (len(rendered_lines) - 1) * 3
        max_line_w = max(r.get_width() for r in rendered_lines)

        base_y = settings.VIRTUAL_HEIGHT - 38 if prompt_active else settings.VIRTUAL_HEIGHT - 22
        bg_rect = pygame.Rect(0, 0, max_line_w + 16, total_h + 8)
        bg_rect.center = (settings.VIRTUAL_WIDTH // 2, base_y - (total_h - rendered_lines[0].get_height()) // 2)

        pygame.draw.rect(surface, (0, 0, 0, 210), bg_rect, border_radius=4)
        pygame.draw.rect(surface, (90, 85, 75), bg_rect, width=1, border_radius=4)

        cur_y = bg_rect.top + 4
        for r in rendered_lines:
            r_rect = r.get_rect(centerx=bg_rect.centerx, top=cur_y)
            surface.blit(r, r_rect)
            cur_y += r.get_height() + 3
