"""
Intro cutscene state (IntroRoadState).
Procedurally animated parallax drive along Carretera Trasandina (Mérida - Barinas),
featuring Gale ParticleSystem smoke, engine failure, player exit, and El Silbón ambush.
"""

import math
import os
import pygame
from gale.input_handler import InputData
from gale.particle_system import ParticleSystem
from gale.state import BaseState
from gale.timer import Timer

import settings
from src.definitions import entity as entity_defs
from src.i18n import t
from src.systems.DiscordManager import discord_rpc
from src.systems.LightingSystem import LightingSystem

# Ambient darkness alpha for the road drive (0.0 = fully clear, 255.0 = pitch black).
# Modify this constant directly to calibrate the cutscene's darkness level.
ROAD_DARKNESS_ALPHA: float = 190.0

# The "driving" phase's fixed length and the "failing" phase's speed
# falloff, mirrored from the phase timeline below.
DRIVING_PHASE_DURATION = 4.0
CAR_DECELERATION = 42.0


class IntroRoadState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.time: float = 0.0
        self.speed: float = 145.0
        self.phase: str = "driving"  # driving -> failing -> stopped -> player_exit -> entering_forest -> ending
        self.skipped: bool = False

        # Ground layout
        self.road_y: float = 170.0
        self.grass_strip_height: float = 134.0

        # Parallax tracking
        self.road_x: float = 0.0
        self.bg_far_x: float = 0.0
        self.bg_mid_x: float = 0.0
        self.bg_close_x: float = 0.0

        # Atmospheric lighting system
        self.lighting = LightingSystem()
        self.lighting.darkness_alpha = ROAD_DARKNESS_ALPHA

        # Assets (loaded first to calibrate dimensions)
        self._load_intro_assets()

        # Tile widths used for seamless scrolling (mod wrapping + tiling step)
        self.road_tile_w: int = self.road_tile.get_width()
        self.grass_tile_w: int = self.grass_tile.get_width()

        # Vehicle
        car_w = self.car_surf.get_width()
        car_h = self.car_surf.get_height()
        self.car_x: float = 110.0
        self.car_y: float = 180.0 + (48.0 - car_h) / 2.0
        self.car_target_y: float = self.car_y
        self.car_shake: float = 0.0

        # The x where the player stops walking right and turns to face north
        self.forest_entry_x: float = self.car_x + car_w + 14.0

        # Player
        self.player_x: float = 0.0
        self.player_y: float = 0.0
        self.player_active: bool = False
        self.player_walking: bool = False
        self.player_scale: float = 1.0

        # Subtitles & narrative cues
        self.sub_text: str = ""
        self.sub_alpha: float = 0.0

        # Gale ParticleSystem for engine smoke (emanates from front hood)
        self.smoke_particles = ParticleSystem(self.car_x + car_w - 8, self.car_y + car_h // 2, n=14)
        self.smoke_particles.set_life_time(0.6, 1.4)
        self.smoke_particles.set_linear_acceleration(-40.0, -25.0, -10.0, -8.0)
        self.smoke_particles.set_area_spread(4.0, 4.0)
        self.smoke_particles.set_colors([
            pygame.Color(40, 40, 45, 180),
            pygame.Color(60, 60, 65, 140),
            pygame.Color(25, 25, 30, 210),
        ])
        self.smoke_spawn_timer: float = 0.0
        self.smoke_active: bool = False

    def _load_intro_assets(self) -> None:
        intro_dir = os.path.join(settings.BASE_DIR, "assets", "graphics", "intro")
        car_path = os.path.join(intro_dir, "car_084.png")
        if not os.path.exists(car_path):
            car_path = os.path.join(intro_dir, "car.png")

        # Car sprite
        if os.path.exists(car_path):
            raw_car = pygame.image.load(car_path)
            if "082" in car_path:
                # car_082.png faces down, rotate 90 deg counter-clockwise to face forward right
                self.car_surf = pygame.transform.rotate(raw_car, 90)
            else:
                self.car_surf = raw_car
        else:
            self.car_surf = pygame.Surface((95, 43))
            self.car_surf.fill((140, 30, 30))

        # Parallax layers and road, back to front. The backdrop is a flat
        # color, so it's stretched to the screen once instead of tiled.
        self.bg_layer = pygame.transform.scale(
            settings.TEXTURES["forest_parallax_bg"], (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        )
        self.far_trees_layer = settings.TEXTURES["forest_parallax_far_trees"]
        self.mid_trees_layer = settings.TEXTURES["forest_parallax_mid_trees"]
        self.close_trees_layer = settings.TEXTURES["forest_parallax_close_trees"]
        self.road_tile = settings.TEXTURES["intro_road"]
        self.grass_tile = settings.TEXTURES["intro_grass"]

        # Player walk animations
        self.player_animations, self.player_textures = entity_defs.build_animations(
            entity_defs.PLAYER_ANIMATIONS, entity_defs.PLAYER_FALLBACK_COLOR, entity_defs.PLAYER_SIZE
        )
        self.current_anim = self.player_animations.get("walk-right")
        self.current_anim_key = self.player_textures.get("walk-right")

    def enter(self, *args, **kwargs) -> None:
        self.time = 0.0
        self.speed = 145.0
        discord_rpc.update(
            details="Prólogo: El Camino del Llano",
            state="Buscando refugio en la tormenta",
            reset_timer=True,
        )
        self.phase = "driving"
        self.skipped = False
        self.sub_text = t("intro_road_state_enter")
        settings.stop_all_audio()
        # Start continuous car driving engine audio
        settings.play_sound("car_running", loops=-1, volume=0.5, channel_name="vehicle")

    def exit(self) -> None:
        Timer.clear()
        settings.stop_all_audio()

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        # Any press on ENTER, SPACE, or ESC skips the intro directly into PlayState
        if input_id in ("enter", "action", "interact", "quit", "pause"):
            self._skip_to_game()

    def _skip_to_game(self) -> None:
        if self.skipped:
            return
        self.skipped = True
        Timer.clear()
        settings.stop_all_audio()
        from src.states.game.IntroForestState import IntroForestState
        self.state_machine.pop()
        self.state_machine.push(IntroForestState(self.state_machine))

    def update(self, dt: float) -> None:
        self.time += dt
        self.lighting.darkness_alpha = ROAD_DARKNESS_ALPHA
        self.lighting.update(dt)

        # Update smoke particles (emanating from front hood)
        if self.smoke_active:
            self.smoke_spawn_timer += dt
            if self.smoke_spawn_timer >= 0.06:
                self.smoke_spawn_timer = 0.0
                car_w = self.car_surf.get_width()
                car_h = self.car_surf.get_height()
                self.smoke_particles.x_mean = self.car_x + car_w - 8
                self.smoke_particles.y_mean = self.car_y + car_h // 2
                self.smoke_particles.generate()
        self.smoke_particles.update(dt)

        # ---------------- Phase Timeline ----------------
        if self.phase == "driving":
            if self.time >= DRIVING_PHASE_DURATION:
                self.phase = "failing"
                self.smoke_active = True
                settings.stop_channel("vehicle")
                settings.play_sound("car_break_and_stop", loops=0, volume=0.65, channel_name="vehicle")
                self.sub_text = t("intro_road_state_failing")
                
        elif self.phase == "failing":
            # Sputter & gradual deceleration down to 0 over 3.5s
            self.car_shake = math.sin(self.time * 35.0) * 1.5
            self.speed = max(0.0, self.speed - CAR_DECELERATION * dt)
            # Pull car over towards the bottom roadside shoulder
            if self.car_y < 134.0:
                self.car_y += 3.0 * dt

            if self.speed <= 0.0:
                self.speed = 0.0
                self.phase = "stopped"
                self.time_stopped = self.time

        elif self.phase == "stopped":
            self.car_shake = 0.0
            if self.time - getattr(self, "time_stopped", self.time) >= 1.2:
                self.phase = "player_exit"
                settings.stop_channel("vehicle")
                self.player_active = True
                self.player_x = self.car_x + 37
                self.player_y = self.car_y - self.car_surf.get_height() - 10
                self.player_walking = True
                self.sub_text = t("intro_road_state_stopped")

        elif self.phase == "player_exit":
            if self.player_walking:
                self.player_x += 16.0 * dt
                self.player_y -= 4.0 * dt
                if self.player_x >= self.forest_entry_x:
                    self.player_walking = False
                    self.current_anim = self.player_animations.get("idle-right")
                    self.current_anim_key = self.player_textures.get("idle-right")
                    self.time_ambush_wait = self.time
                    # Player pauses in the dark silence by the roadside
                    def _start_whistle() -> None:
                        if self.skipped or self.phase != "player_exit":
                            return
                        settings.play_sound("whistle", volume=0.08, channel_name="silbon_whistle")

                    def _ask_who() -> None:
                        if self.skipped or self.phase != "player_exit":
                            return
                        self.sub_text = t("intro_road_state_ask_who")

                    Timer.after(0.5, _start_whistle)
                    Timer.after(1.6, _ask_who)

            elif hasattr(self, "time_ambush_wait") and (self.time - self.time_ambush_wait >= 4.5):
                self.phase = "entering_forest"
                self.time_entering_forest = self.time
                self.player_walking = True
                self.sub_text = ""
                self.current_anim = self.player_animations.get("walk-up")
                self.current_anim_key = self.player_textures.get("walk-up")

        elif self.phase == "entering_forest":
            # Walks north into the tree line, shrinking as it goes to read
            # as moving away into the distance rather than just upward.
            entering_duration = 2.2
            lerp_t = min((self.time - self.time_entering_forest) / entering_duration, 1.0)
            self.player_y -= 16.0 * dt
            self.player_scale = 1.0 - 0.8 * lerp_t

            if lerp_t >= 1.0:
                self.player_walking = False
                self.phase = "ending"
                Timer.after(1.0, self._skip_to_game)

        # Update player animation
        if self.player_active and self.current_anim:
            self.current_anim.update(dt)

        # Update Parallax scrolling (only when speed > 0)
        if self.speed > 0.0:
            self.road_x = (self.road_x - self.speed * dt) % self.road_tile_w
            self.bg_far_x = (self.bg_far_x - self.speed * 0.12 * dt) % 592
            self.bg_mid_x = (self.bg_mid_x - self.speed * 0.28 * dt) % 592
            self.bg_close_x = (self.bg_close_x - self.speed * 0.5 * dt) % 592

    def _headlight_cone_points(self, origin, length: float, spread_deg: float, steps: int = 12):
        """
        A fan of points around an arc instead of a flat triangle, so the
        far edge of the beam reads as a curve like the flashlight's cone
        does, rather than a straight cut.
        """
        half = math.radians(spread_deg / 2.0)
        points = [origin]
        for i in range(steps + 1):
            angle = -half + i * (2.0 * half / steps)
            points.append((origin[0] + length * math.cos(angle), origin[1] + length * math.sin(angle)))
        return points

    def render(self, surface: pygame.Surface) -> None:
        # Forest backdrop, back to front.
        road_y = self.road_y
        surface.blit(self.bg_layer, (0, 0))
        for tx in range(-592, settings.VIRTUAL_WIDTH + 592, 592):
            surface.blit(self.far_trees_layer, (tx + round(self.bg_far_x), road_y - self.far_trees_layer.get_height()))
        for tx in range(-592, settings.VIRTUAL_WIDTH + 592, 592):
            surface.blit(self.mid_trees_layer, (tx + round(self.bg_mid_x), road_y - self.mid_trees_layer.get_height()))
        for tx in range(-592, settings.VIRTUAL_WIDTH + 592, 592):
            surface.blit(self.close_trees_layer, (tx + round(self.bg_close_x), road_y - self.close_trees_layer.get_height()))

        for tx in range(-self.grass_tile_w, settings.VIRTUAL_WIDTH + self.grass_tile_w, self.grass_tile_w):
            surface.blit(self.grass_tile, (tx + round(self.road_x), road_y - self.grass_strip_height))

        # Seamless road tiling
        for tx in range(-self.road_tile_w, settings.VIRTUAL_WIDTH + self.road_tile_w, self.road_tile_w):
            surface.blit(self.road_tile, (tx + round(self.road_x), road_y))

        # Car vehicle
        surface.blit(self.car_surf, (round(self.car_x), round(self.car_y + self.car_shake)))

        # Player sprite (if stepped out)
        if self.player_active and self.current_anim:
            frame = self.current_anim.get_current_frame()
            tex = settings.TEXTURES.get(self.current_anim_key)
            if tex and isinstance(frame, pygame.Rect):
                if self.player_scale == 1.0:
                    surface.blit(tex, (round(self.player_x), round(self.player_y)), frame)
                else:
                    fw, fh = frame.width, frame.height
                    scaled_size = (max(1, round(fw * self.player_scale)), max(1, round(fh * self.player_scale)))
                    sprite = pygame.transform.scale(tex.subsurface(frame), scaled_size)
                    sw, sh = sprite.get_size()
                    surface.blit(sprite, (round(self.player_x + fw / 2 - sw / 2), round(self.player_y + fh - sh)))
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (round(self.player_x), round(self.player_y)))
            else:
                pygame.draw.rect(surface, entity_defs.PLAYER_FALLBACK_COLOR, (round(self.player_x), round(self.player_y), 16, 32))

        # Smoke particles (from engine hood)
        self.smoke_particles.render(surface)

        # Headlights geometry: carve out darkness so the road in front is clear
        headlight_carve = []
        headlight_cones = []
        if self.speed > 0.0 or self.phase in ("driving", "failing", "stopped", "player_exit"):
            car_w = self.car_surf.get_width()
            car_h = self.car_surf.get_height()
            p_front1 = (self.car_x + car_w - 4, self.car_y + car_h // 2 + self.car_shake - 8)
            p_front2 = (self.car_x + car_w - 4, self.car_y + car_h // 2 + self.car_shake + 8)

            cone1_outer = self._headlight_cone_points(p_front1, 190, 26.6)
            cone1_inner = self._headlight_cone_points(p_front1, 130, 21.7)
            cone2_outer = self._headlight_cone_points(p_front2, 190, 26.6)
            cone2_inner = self._headlight_cone_points(p_front2, 130, 21.7)

            # Polygons and alphas carved out of the ambient darkness
            headlight_carve = [
                (cone1_outer, 180),
                (cone1_inner, 255),
                (cone2_outer, 180),
                (cone2_inner, 255),
            ]
            headlight_cones = [
                (cone1_outer, (255, 245, 180, 45)),
                (cone1_inner, (255, 245, 180, 100)),
                (cone2_outer, (255, 245, 180, 45)),
                (cone2_inner, (255, 245, 180, 100)),
            ]

        # Atmospheric night darkness overlay via LightingSystem
        self.lighting.render(surface, player=None, custom_light_polygons=headlight_carve)

        # Draw headlights beam over the scene (unaffected and radiant over the illuminated road)
        if headlight_cones:
            light_beam = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            for pts, color in headlight_cones:
                pygame.draw.polygon(light_beam, color, pts)
            surface.blit(light_beam, (0, 0))

        # Subtitles & HUD skip prompt
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
        skip_text = t("intro_forest_skip")
        skip_surf = skip_f.render(skip_text, True, (160, 155, 140))
        surface.blit(skip_surf, (settings.VIRTUAL_WIDTH - skip_surf.get_width() - 10, 8))