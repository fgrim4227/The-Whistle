"""
Monster entity class (El Silbón). AI decision-making lives in the
per-state classes under src/states/entity/ (Patrol, MovingToDoor,
Knocking, Chase, Investigate, Berserk, Stunned); this class only holds
the entity's own data and the movement/animation/rendering it exposes
to those states.
"""

import math
import random
from typing import Dict, List, Tuple

import pygame
from gale.animation import Animation
from gale.state import StateMachine

import settings
from src.commands import BERSERK
from src.definitions import entity as entity_defs
from src.entities.BaseEntity import BaseEntity
from src.states.entity.monster.MonsterBerserkState import MonsterBerserkState
from src.states.entity.monster.MonsterChaseState import MonsterChaseState
from src.states.entity.monster.MonsterInvestigateState import MonsterInvestigateState
from src.states.entity.monster.MonsterKnockingState import MonsterKnockingState
from src.states.entity.monster.MonsterMovingToDoorState import MonsterMovingToDoorState
from src.states.entity.monster.MonsterPatrolState import MonsterPatrolState
from src.states.entity.monster.MonsterStunnedState import MonsterStunnedState
from src.states.entity.monster.MonsterStalkingState import MonsterStalkingState


class Monster(BaseEntity):
    def __init__(self, x: float, y: float, start_room: str = "hallway") -> None:
        width, height = entity_defs.MONSTER_SIZE
        super().__init__(x, y, width=width, height=height, speed=settings.MONSTER_PATROL_SPEED)
        self.current_room_name = start_room
        self.target_x = x
        self.target_y = y
        self.current_wp_idx = 0
        self.distance_to_player = 9999.0
        self.is_moving = False

        self.animations: Dict[str, Animation]
        self._animation_textures: Dict[str, str]
        self.animations, self._animation_textures = self._create_animations()
        self.current_animation_name = "idle"
        self.current_animation = self.animations.get("idle")
        self.current_texture = self._animation_textures.get("idle")

        self.state_machine = StateMachine({
            "patrol": lambda sm: MonsterPatrolState(self, sm),
            "moving_to_door": lambda sm: MonsterMovingToDoorState(self, sm),
            "investigate": lambda sm: MonsterInvestigateState(self, sm),
            "knocking": lambda sm: MonsterKnockingState(self, sm),
            "chase": lambda sm: MonsterChaseState(self, sm),
            "berserk": lambda sm: MonsterBerserkState(self, sm),
            "stunned": lambda sm: MonsterStunnedState(self, sm),
            "stalking": lambda sm: MonsterStalkingState(self, sm),
        })
        self.ai_state = "patrol"
        self.state_machine.change(self.ai_state)

    def change_state(self, state_name: str, *args, **kwargs) -> None:
        self.state_machine.change(state_name, *args, **kwargs)
        self.ai_state = state_name

    def _create_animations(self) -> Tuple[Dict[str, Animation], Dict[str, str]]:
        return entity_defs.build_animations(
            entity_defs.MONSTER_ANIMATIONS, entity_defs.MONSTER_FALLBACK_COLOR, entity_defs.MONSTER_SPRITE_SIZE
        )

    def change_animation(self, anim_name: str) -> None:
        if anim_name in self.animations and self.current_animation != self.animations[anim_name]:
            self.current_animation = self.animations[anim_name]
            self.current_animation.reset()
            self.current_texture = self._animation_textures.get(anim_name)
            self.current_animation_name = anim_name

    def hear_noise(self, noise_x: float, noise_y: float, radius: float = 280.0) -> None:
        """Alerts the monster of a sound if within audio radius."""
        if self.ai_state in ("stunned", "berserk", "knocking"):
            return

        dist = math.hypot(noise_x - self.x, noise_y - self.y)
        if dist <= radius:
            self.change_state("investigate", target_x=noise_x, target_y=noise_y)

    def receive_throw_hit(self) -> str:
        """Applies 75% Stun / 25% Berserk probability."""
        roll = random.random()
        if roll < settings.THROW_BERSERK_CHANCE:
            BERSERK(self)
            return "berserk"
        else:
            duration = random.uniform(3.0, 4.5)
            self.change_state("stunned", duration=duration)
            return "stunned"

    def has_line_of_sight(self, target_x: float, target_y: float, obstacles: List[pygame.Rect]) -> bool:
        """Whether nothing solid stands between this monster and a point."""
        mx, my = self.get_collision_center()
        return not any(obs.clipline(mx, my, target_x, target_y) for obs in obstacles)

    def can_detect_player(self, player, house) -> bool:
        """
        Whether the player can be seen right now: close enough to make out,
        and with a clear line to them. Sound is a separate sense, handled by
        hear_noise(), and walls don't stop it.
        """
        if player.is_hidden:
            return False

        px, py = player.get_center()
        mx, my = self.get_center()
        self.distance_to_player = math.hypot(px - mx, py - my)

        view_distance = 210.0 if player.flashlight_on else 85.0
        if self.distance_to_player > view_distance:
            return False

        room = house.rooms.get(self.current_room_name)
        obstacles = room.get_obstacles() if room else []
        return self.has_line_of_sight(px, py, obstacles)


    def move_towards(self, target_x: float, target_y: float, obstacles: List[pygame.Rect], dt: float) -> None:
        """
        Moves towards target coordinate with obstacle avoidance. This is
        purely mechanical: it takes one step toward whatever point it's
        given and resolves collision against it. It never decides "I've
        arrived, go idle" on its own, because every AI state shares this
        one call and passes it either the real destination or just the
        next stop along a route -- only the state itself knows which one
        that is and what should happen once it's actually reached.

        Steering is measured from the collision box rather than the
        sprite's geometric middle, since that box is both what routes are
        planned around and what obstacles are tested against.
        """
        mx, my = self.get_collision_center()
        dx = target_x - mx
        dy = target_y - my
        dist = math.hypot(dx, dy)

        if dist < 0.5:
            # Close enough that there's no meaningful direction left to
            # normalize -- avoid a division by zero, nothing else to do.
            self.vx = 0.0
            self.vy = 0.0
            return

        self.is_moving = True
        nx = dx / dist
        ny = dy / dist
        self.vx = nx * self.speed
        self.vy = ny * self.speed

        if abs(nx) > abs(ny):
            self.direction = "right" if nx > 0 else "left"
        else:
            self.direction = "down" if ny > 0 else "up"

        self.change_animation(f"walk-{self.direction}")

        new_x = self.x + nx * self.speed * dt
        rect_x = self.get_collision_rect(x=new_x)
        if not any(rect_x.colliderect(obs) for obs in obstacles):
            self.x = new_x

        new_y = self.y + ny * self.speed * dt
        rect_y = self.get_collision_rect(y=new_y)
        if not any(rect_y.colliderect(obs) for obs in obstacles):
            self.y = new_y


    def update_ai(self, player, house, dt: float) -> None:
        self.state_machine.current.process_ai(house, player, dt)

        if self.current_animation:
            self.current_animation.update(dt)


    def get_collision_rect(self, x: float = None, y: float = None) -> pygame.Rect:
        rx = self.x if x is None else x
        ry = self.y if y is None else y
        return pygame.Rect(int(rx), int(ry + 16), self.width, self.height - 16)

    def get_collision_center(self) -> Tuple[float, float]:
        rect = self.get_collision_rect()
        return (rect.centerx, rect.centery)

    def get_route_widths(self) -> Tuple[float, float]:
        """
        The body width a route is planned against, as (preferred, minimum).

        The minimum is the longest side of the collision box: the safety
        margin around obstacles grows by the same amount horizontally and
        vertically, so measuring by the sprite's width alone would plan
        routes through gaps the body is too tall to fit through. The
        preferred width adds a little on top, so a route rounds a corner
        with room to spare and only squeezes past when there's no other way.
        """
        rect = self.get_collision_rect()
        body = float(max(rect.width, rect.height))
        return body + 4.0, body

    def render_sprite(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Renders the current animation frame horizontally centered over the
        collision box, bottom-anchored a fixed margin below it. Computed
        from the frame's own size (rather than a fixed offset) so idle's
        smaller 64x64 sheet and walk/running's 92x92 sheets don't visually
        jump position when the animation changes.
        """
        ox, oy = camera_offset

        frame = self.current_animation.get_current_frame() if self.current_animation else None
        frame_size = None
        if isinstance(frame, pygame.Rect):
            frame_size = (frame.width, frame.height)
        elif isinstance(frame, pygame.Surface):
            frame_size = frame.get_size()

        if frame_size is None:
            pygame.draw.rect(surface, entity_defs.MONSTER_FALLBACK_COLOR, self.get_rect().move(-ox, -oy))
            return

        fw, fh = frame_size
        sprite_x = int(self.x - ox + (self.width - fw) / 2)
        sprite_y = int(self.y - oy + self.height - fh + entity_defs.MONSTER_SPRITE_BOTTOM_MARGIN)

        if isinstance(frame, pygame.Rect):
            surface.blit(settings.TEXTURES[self.current_texture], (sprite_x, sprite_y), frame)
        else:
            surface.blit(frame, (sprite_x, sprite_y))

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        self.state_machine.current.render(surface, camera_offset)
