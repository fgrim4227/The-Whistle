"""
Intro cutscene state (IntroForestState).
Picks up right where IntroRoadState leaves off, once the player has
walked into the tree line.
"""

import pygame
from gale.input_handler import InputData
from gale.state import BaseState
from gale.timer import Timer

import settings
from src.definitions import entity as entity_defs

# How fast the player walks up into the clearing, in pixels per second.
PLAYER_ENTRY_SPEED = 24.0

# How long each line of dialogue stays on screen before the next one
# takes over -- enough time to read a short sentence.
LINE_DISPLAY_DURATION = 3.0

# How far above the player El Silbón first appears, how fast it walks
# down toward them, and how close it gets before holding still.
MONSTER_START_OFFSET_Y = 70.0
MONSTER_APPROACH_SPEED = 20.0
MONSTER_STOP_DISTANCE = 40.0

# How long the punch sound gets to play before the screen cuts to black.
BLACKOUT_DELAY = 0.5


class IntroForestState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.time: float = 0.0
        self.phase: str = "entering"  # entering -> line1 -> line2 -> monster_approach -> done -> blackout
        self.skipped: bool = False
        self.line_timer: float = 0.0
        self.done_timer: float = 0.0
        self.sub_text: str = ""
        self.monster_active: bool = False
        self.monster_x: float = 0.0
        self.monster_y: float = 0.0
        self.monster_current_anim = None
        self.monster_current_anim_key = None

        self._load_assets()

        # Walks up from just below the bottom edge to the middle of the
        # screen, centered horizontally, then stops.
        self.player_x: float = settings.VIRTUAL_WIDTH / 2.0 - entity_defs.PLAYER_SIZE[0] / 2.0 - 30
        self.player_y: float = float(settings.VIRTUAL_HEIGHT)
        self.player_target_y: float = settings.VIRTUAL_HEIGHT / 2.0
        self.current_anim = self.player_animations.get("walk-up")
        self.current_anim_key = self.player_textures.get("walk-up")

    def _load_assets(self) -> None:
        self.background = settings.TEXTURES["intro_forest_bg"]
        self.player_animations, self.player_textures = entity_defs.build_animations(
            entity_defs.PLAYER_ANIMATIONS, entity_defs.PLAYER_FALLBACK_COLOR, entity_defs.PLAYER_SIZE
        )
        self.monster_animations, self.monster_textures = entity_defs.build_animations(
            entity_defs.MONSTER_ANIMATIONS, entity_defs.MONSTER_FALLBACK_COLOR, entity_defs.MONSTER_SPRITE_SIZE
        )

    def enter(self, *args, **kwargs) -> None:
        self.time = 0.0
        self.phase = "entering"
        self.skipped = False

    def exit(self) -> None:
        Timer.clear()
        settings.stop_all_audio()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("enter", "action", "interact", "quit", "pause"):
            self._skip_to_game()

    def _skip_to_game(self) -> None:
        if self.skipped:
            return
        self.skipped = True
        Timer.clear()
        settings.stop_all_audio()
        from src.states.game.PlayState import PlayState
        self.state_machine.pop()
        self.state_machine.push(PlayState(self.state_machine))

    def update(self, dt: float) -> None:
        self.time += dt

        if self.current_anim:
            self.current_anim.update(dt)

        if self.phase == "entering":
            self.player_y -= PLAYER_ENTRY_SPEED * dt
            if self.player_y <= self.player_target_y:
                self.player_y = self.player_target_y
                self.phase = "line1"
                self.current_anim = self.player_animations.get("idle-down")
                self.current_anim_key = self.player_textures.get("idle-down")
                self.sub_text = "Qué raro, creí oír a alguien por aquí..." if not settings.IS_ENGLISH else "Strange, I thought I heard someone around here...."

        elif self.phase == "line1":
            self.line_timer += dt
            if self.line_timer >= LINE_DISPLAY_DURATION:
                self.line_timer = 0.0
                self.phase = "line2"
                self.sub_text = "Intentaré hacer una llamada..." if not settings.IS_ENGLISH else "I'll try to make a call..."
                settings.play_sound("whistle", volume=0.01, channel_name="silbon_whistle")

        elif self.phase == "line2":
            self.line_timer += dt
            if self.line_timer >= LINE_DISPLAY_DURATION:
                self.line_timer = 0.0
                self.phase = "monster_approach"
                self.sub_text = ""
                self.monster_active = True
                self.monster_x = (
                    self.player_x + entity_defs.PLAYER_SIZE[0] / 2.0 - entity_defs.MONSTER_SPRITE_SIZE[0] / 2.0
                )
                self.monster_y = self.player_y - MONSTER_START_OFFSET_Y
                self.monster_current_anim = self.monster_animations.get("walk-down")
                self.monster_current_anim_key = self.monster_textures.get("walk-down")

        elif self.phase == "monster_approach":
            if self.monster_current_anim:
                self.monster_current_anim.update(dt)

            self.monster_y += MONSTER_APPROACH_SPEED * dt/2
            if self.monster_y >= self.player_y - MONSTER_STOP_DISTANCE:
                self.monster_y = self.player_y - MONSTER_STOP_DISTANCE
                self.phase = "done"
                self.done_timer = 0.0
                settings.play_sound("punch", volume=0.85, channel_name="sfx")

        elif self.phase == "done":
            self.done_timer += dt
            if self.done_timer >= BLACKOUT_DELAY:
                self.phase = "blackout"
                self.done_timer = 0.0

        elif self.phase == "blackout":
            self.done_timer += dt
            if self.done_timer >= 4.0:
                self._skip_to_game()

    def render(self, surface: pygame.Surface) -> None:
        if self.phase == "blackout":
            surface.fill((0, 0, 0))
            font = settings.FONTS.get("medium", settings.FONTS["small"])
            t1 = (
                "Algo te ha intentado matar pero lograste sobrevivir." if not settings.IS_ENGLISH
                else "Something tried to kill you, but you managed to survive."
            )
            t2 = "Despiertas en otro lugar..." if not settings.IS_ENGLISH else "You wake up somewhere else..."
            s1 = font.render(t1, True, (235, 235, 235))
            s2 = font.render(t2, True, (235, 235, 235))
            surface.blit(s1, (settings.VIRTUAL_WIDTH // 2 - s1.get_width() // 2, settings.VIRTUAL_HEIGHT // 2 - 14))
            surface.blit(s2, (settings.VIRTUAL_WIDTH // 2 - s2.get_width() // 2, settings.VIRTUAL_HEIGHT // 2 + 10))
            return

        surface.blit(self.background, (0, 0))

        if self.monster_active and self.monster_current_anim:
            frame = self.monster_current_anim.get_current_frame()
            tex = settings.TEXTURES.get(self.monster_current_anim_key)
            if tex and isinstance(frame, pygame.Rect):
                surface.blit(tex, (round(self.monster_x), round(self.monster_y)), frame)
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (round(self.monster_x), round(self.monster_y)))
            else:
                pygame.draw.rect(
                    surface, entity_defs.MONSTER_FALLBACK_COLOR,
                    (round(self.monster_x), round(self.monster_y), *entity_defs.MONSTER_SPRITE_SIZE),
                )

        if self.current_anim:
            frame = self.current_anim.get_current_frame()
            tex = settings.TEXTURES.get(self.current_anim_key)
            if tex and isinstance(frame, pygame.Rect):
                surface.blit(tex, (round(self.player_x), round(self.player_y)), frame)
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (round(self.player_x), round(self.player_y)))
            else:
                pygame.draw.rect(
                    surface, entity_defs.PLAYER_FALLBACK_COLOR,
                    (round(self.player_x), round(self.player_y), *entity_defs.PLAYER_SIZE),
                )

        if self.sub_text:
            font = settings.FONTS.get("dialogue", settings.FONTS["small"])
            sub_surf = font.render(self.sub_text, True, (240, 235, 220))
            sub_rect = sub_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 22))
            bg_rect = sub_rect.inflate(16, 6)
            pygame.draw.rect(surface, (8, 8, 14, 210), bg_rect, border_radius=4)
            pygame.draw.rect(surface, (120, 100, 60), bg_rect, width=1, border_radius=4)
            surface.blit(sub_surf, sub_rect)


         # Skip indicator in top-right
        skip_f = settings.FONTS.get("hud", settings.FONTS["small"])
        skip_text = "[ENTER: Omitir]" if not settings.IS_ENGLISH else "[ENTER: Skip]"
        skip_surf = skip_f.render(skip_text, True, (160, 155, 140))
        surface.blit(skip_surf, (settings.VIRTUAL_WIDTH - skip_surf.get_width() - 10, 8))
