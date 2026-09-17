"""
Intro cutscene state (IntroRoadState).
Procedurally animated parallax drive along Carretera Trasandina (Mérida - Barinas),
featuring Gale ParticleSystem smoke, engine failure, player exit, and El Silbón ambush.
"""

import math
import os
import random
from typing import List
import pygame
from gale.animation import Animation
from gale.input_handler import InputData
from gale.particle_system import ParticleSystem
from gale.state import BaseState
from gale.timer import Timer

import settings
from src.definitions import entity as entity_defs
from src.i18n import t


class RoadsidePlant:
    """A small bush/tree scrolling across the grass strip at ground speed."""

    def __init__(self, x: float, y: float, surf: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.surf = surf

    def update(self, dt: float, speed: float) -> None:
        self.x -= speed * dt

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.surf, (round(self.x), round(self.y)))


class IntroRoadState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.time: float = 0.0
        self.speed: float = 145.0
        self.phase: str = "driving"  # driving -> failing -> stopped -> player_exit -> entering_forest -> ambush -> black
        self.skipped: bool = False

        # Ground layout, shared between render() and the plant seeding below
        self.road_y: float = 170.0
        self.grass_strip_height: float = 45.0

        # Parallax tracking
        self.road_x: float = 0.0
        self.bg_far_x: float = 0.0
        self.bg_mid_x: float = 0.0
        self.bg_close_x: float = 0.0

        # Assets (loaded first to calibrate dimensions)
        self._load_intro_assets()

        # Roadside plants scattered over the grass strip, thickening the
        # feel of the forest right from the drive-in
        self.plants: List[RoadsidePlant] = [
            RoadsidePlant(
                random.uniform(0, settings.VIRTUAL_WIDTH),
                self.road_y - random.uniform(10, self.grass_strip_height),
                random.choice(self.plant_surfs),
            )
            for _ in range(10)
        ]

        # Vehicle
        car_w = self.car_surf.get_width()
        car_h = self.car_surf.get_height()
        self.car_x: float = 110.0
        self.car_y: float = 180.0 + (48.0 - car_h) / 2.0
        self.car_target_y: float = self.car_y
        self.car_shake: float = 0.0

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
        car_path = os.path.join(intro_dir, "car_082.png")
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
        self.plant_surfs = [
            settings.TEXTURES["intro_plant_1"],
            settings.TEXTURES["intro_plant_2"],
            settings.TEXTURES["intro_plant_3"],
        ]

        # Player walk animations
        self.player_animations, self.player_textures = entity_defs.build_animations(
            entity_defs.PLAYER_ANIMATIONS, entity_defs.PLAYER_FALLBACK_COLOR, entity_defs.PLAYER_SIZE
        )
        self.current_anim = self.player_animations.get("walk-right")
        self.current_anim_key = self.player_textures.get("walk-right")

    def enter(self, *args, **kwargs) -> None:
        self.time = 0.0
        self.speed = 145.0
        self.phase = "driving"
        self.skipped = False
        self.sub_text = "Carretera Trasandina, Mérida - Barinas (2:14 AM)" if not settings.IS_ENGLISH else "Trasandina Highway, Mérida - Barinas (2:14 AM)"

    def enter(self, *args, **kwargs) -> None:
        self.time = 0.0
        self.speed = 145.0
        self.phase = "driving"
        self.skipped = False
        self.sub_text = "Carretera Trasandina, Mérida - Barinas (2:14 AM)" if not settings.IS_ENGLISH else "Trasandina Highway, Mérida - Barinas (2:14 AM)"
        settings.stop_all_audio()
        # Start continuous car driving engine audio
        settings.play_sound("car_running", loops=-1, volume=0.5, channel_name="vehicle")

    def exit(self) -> None:
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
        settings.stop_all_audio()
        from src.states.game.PlayState import PlayState
        self.state_machine.pop()
        self.state_machine.push(PlayState(self.state_machine))

    def update(self, dt: float) -> None:
        self.time += dt

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
            # Normal driving for first 4 seconds
            if self.time >= 4.0:
                self.phase = "failing"
                self.smoke_active = True
                # Switch from car_running loop to car_break_and_stop
                settings.stop_channel("vehicle")
                settings.play_sound("car_break_and_stop", loops=0, volume=0.65, channel_name="vehicle")
                self.sub_text = "¡El motor comenzó a fallar...!" if not settings.IS_ENGLISH else "The engine started sputtering...!"

        elif self.phase == "failing":
            # Sputter & gradual deceleration down to 0 over 3.5s
            self.car_shake = math.sin(self.time * 35.0) * 1.5
            self.speed = max(0.0, self.speed - 42.0 * dt)
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
                # Stop car sounds: the player turns off the vehicle before stepping out
                settings.stop_channel("vehicle")
                self.player_active = True
                self.player_x = self.car_x + 37
                self.player_y = self.car_y - self.car_surf.get_height() - 10
                self.player_walking = True
                self.sub_text = "Maldición... el radiador hirvió. No hay señal aquí." if not settings.IS_ENGLISH else "Damn it... radiator boiled over. No phone signal out here."

        elif self.phase == "player_exit":
            if self.player_walking:
                self.player_x += 16.0 * dt
                self.player_y -= 4.0 * dt
                if self.player_x >= self.car_x + self.car_surf.get_width() + 14:
                    self.player_walking = False
                    self.current_anim = self.player_animations.get("idle-right")
                    self.current_anim_key = self.player_textures.get("idle-right")
                    self.time_ambush_wait = self.time
                    # Player pauses in the dark silence by the roadside
                    def _start_whistle() -> None:
                        channel = settings.play_sound("whistle", volume=0.05, channel_name="silbon_whistle")

                        def _end_whistle() -> None:
                            if channel:
                                channel.stop()
                            self.sub_text = "¿Quién anda ahí...? ¿Hay alguien?" if not settings.IS_ENGLISH else "Who's out there...? Anyone around?"

                        Timer.after(5.5, _end_whistle)

                    Timer.after(0.5, _start_whistle)

            elif hasattr(self, "time_ambush_wait") and (self.time - self.time_ambush_wait >= 2.5):
                self.phase = "entering_forest"
                self.time_entering_forest = self.time
                self.player_walking = True
                self.current_anim = self.player_animations.get("walk-up")
                self.current_anim_key = self.player_textures.get("walk-up")

        elif self.phase == "entering_forest":
            # Walks north into the tree line, shrinking as it goes to read
            # as moving away into the distance rather than just upward.
            entering_duration = 2.2
            t = min((self.time - self.time_entering_forest) / entering_duration, 1.0)
            self.player_y -= 16.0 * dt
            self.player_scale = 1.0 - 0.8 * t

            if t >= 1.0:
                self.player_walking = False
                self.phase = "ambush"
                self.time_ambush = self.time
                # Jumpscare attack
                #settings.play_sound("jumpscare1", volume=0.85, channel_name="jumpscare1")
                settings.play_sound("knock_door", volume=0.95, channel_name="sfx")

        elif self.phase == "ambush":
            if self.time - getattr(self, "time_ambush", self.time) >= 0.25:
                self.phase = "black"
                self.time_black = self.time

        elif self.phase == "black":
            # Fade in blackout transition text
            elapsed = self.time - getattr(self, "time_black", self.time)
            if elapsed >= 3.5:
                self._skip_to_game()

        # Update player animation
        if self.player_active and self.current_anim:
            self.current_anim.update(dt)

        # Update Parallax scrolling (only when speed > 0)
        if self.speed > 0.0:
            self.road_x = (self.road_x - self.speed * dt) % 64
            self.bg_far_x = (self.bg_far_x - self.speed * 0.12 * dt) % 592
            self.bg_mid_x = (self.bg_mid_x - self.speed * 0.28 * dt) % 592
            self.bg_close_x = (self.bg_close_x - self.speed * 0.5 * dt) % 592

            for plant in self.plants:
                plant.update(dt, self.speed)
                if plant.x < -plant.surf.get_width():
                    plant.x = settings.VIRTUAL_WIDTH + random.uniform(0, 40)
                    plant.y = self.road_y - random.uniform(10, self.grass_strip_height) + 100
                    plant.surf = random.choice(self.plant_surfs)

    def render(self, surface: pygame.Surface) -> None:
        if self.phase == "black":
            # Pitch black screen with story transition text
            surface.fill((0, 0, 0))
            elapsed = self.time - getattr(self, "time_black", self.time)
            alpha = min(255, int(elapsed * 120))

            t1 = "Horas más tarde..." if not settings.IS_ENGLISH else "Hours later..."
            t2 = "Despiertas encerrado en una vieja cabaña." if not settings.IS_ENGLISH else "You wake up locked inside a secluded cabin."

            f_large = settings.FONTS.get("large", settings.FONTS["medium"])
            f_small = settings.FONTS.get("small", settings.FONTS["medium"])

            s1 = f_large.render(t1, True, (220, 215, 200))
            s2 = f_small.render(t2, True, (160, 40, 30))

            surface.blit(s1, (settings.VIRTUAL_WIDTH // 2 - s1.get_width() // 2, settings.VIRTUAL_HEIGHT // 2 - 20))
            surface.blit(s2, (settings.VIRTUAL_WIDTH // 2 - s2.get_width() // 2, settings.VIRTUAL_HEIGHT // 2 + 15))

            skip_hint = f_small.render("[ENTER / ESPACIO]" if not settings.IS_ENGLISH else "[ENTER / SPACE]", True, (90, 85, 80))
            surface.blit(skip_hint, (settings.VIRTUAL_WIDTH - skip_hint.get_width() - 15, settings.VIRTUAL_HEIGHT - 22))
            return

        # 1. Forest backdrop, back to front. Each tree layer is taller than
        # the strip of sky above the road, so it's anchored by its own
        # bottom edge to that strip instead of by its top -- otherwise
        # only the sparse upper fringe of the canopy would ever show, with
        # the dense treeline hidden below the road.
        road_y = self.road_y
        surface.blit(self.bg_layer, (0, 0))
        for tx in range(-592, settings.VIRTUAL_WIDTH + 592, 592):
            surface.blit(self.far_trees_layer, (tx + round(self.bg_far_x), road_y - self.far_trees_layer.get_height()))
        for tx in range(-592, settings.VIRTUAL_WIDTH + 592, 592):
            surface.blit(self.mid_trees_layer, (tx + round(self.bg_mid_x), road_y - self.mid_trees_layer.get_height()))
        for tx in range(-592, settings.VIRTUAL_WIDTH + 592, 592):
            surface.blit(self.close_trees_layer, (tx + round(self.bg_close_x), road_y - self.close_trees_layer.get_height()))

        pygame.draw.rect(surface, (18, 36, 20), (0, road_y - self.grass_strip_height, settings.VIRTUAL_WIDTH, self.grass_strip_height))

        # 2. Roadside plants, scattered over the grass strip
        for plant in self.plants:
            plant.render(surface)


        # Seamless road tiling
        for tx in range(-64, settings.VIRTUAL_WIDTH + 64, 64):
            surface.blit(self.road_tile, (tx + round(self.road_x), road_y))

        # 3. Headlights beam (projecting forward onto dark road)
        if self.speed > 0.0 or self.phase in ("driving", "failing", "stopped", "player_exit"):
            light_beam = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            car_w = self.car_surf.get_width()
            car_h = self.car_surf.get_height()
            p_front = (self.car_x + car_w - 4, self.car_y + car_h // 2 + self.car_shake)
            pygame.draw.polygon(
                light_beam,
                (255, 245, 180, 45),
                [p_front, (p_front[0] + 190, p_front[1] - 45), (p_front[0] + 190, p_front[1] + 45)],
            )
            pygame.draw.polygon(
                light_beam,
                (255, 245, 180, 100),
                [p_front, (p_front[0] + 130, p_front[1] - 25), (p_front[0] + 130, p_front[1] + 25)],
            )
            surface.blit(light_beam, (0, 0))

        # 4. Car vehicle
        surface.blit(self.car_surf, (round(self.car_x), round(self.car_y + self.car_shake)))

        # 5. Player sprite (if stepped out)
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
                    # Anchored by the feet, so shrinking reads as walking
                    # away instead of the sprite drifting off its own spot.
                    surface.blit(sprite, (round(self.player_x + fw / 2 - sw / 2), round(self.player_y + fh - sh)))
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (round(self.player_x), round(self.player_y)))
            else:
                pygame.draw.rect(surface, entity_defs.PLAYER_FALLBACK_COLOR, (round(self.player_x), round(self.player_y), 16, 32))

        # 6. Smoke particles (from engine hood)
        self.smoke_particles.render(surface)

        # 7. Ambient night darkness vignette
        darkness = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        darkness.fill((6, 8, 14, 130))
        surface.blit(darkness, (0, 0))

        # Jumpscare flash during ambush
        if self.phase == "ambush":
            flash = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            flash.fill((180, 0, 0, 190))
            surface.blit(flash, (0, 0))

        # 8. Subtitles & HUD skip prompt
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
