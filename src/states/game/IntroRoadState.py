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

PLANT_SPAWN_INTERVAL = 0.2

# How far apart, in pixels, two plants in the same row may land -- kept
# small so a row still reads as one line instead of a scatter.
PLANT_ROW_JITTER = 8.0

# Half-width, in pixels, of the reserved opening around forest_entry_x --
# no plant is ever created if it would end up resting inside this band.
FOREST_GAP_HALF_WIDTH = 80.0

# The "driving" phase's fixed length and the "failing" phase's speed
# falloff, mirrored from the phase timeline below so a plant's eventual
# resting spot (once everything has fully stopped) can be worked out at
# the moment it's created.
DRIVING_PHASE_DURATION = 4.0
CAR_DECELERATION = 42.0


class RoadsidePlant:
    """A small bush/tree scrolling across the grass strip at ground speed."""

    def __init__(self, x: float, y: float, surf: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.surf = surf

    def update(self, dt: float, speed: float) -> None:
        self.x -= speed * dt

    def is_out_of_game(self) -> bool:
        return self.x < -self.surf.get_width()

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.surf, (round(self.x), round(self.y)))


class IntroRoadState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.time: float = 0.0
        self.speed: float = 145.0
        self.phase: str = "driving"  # driving -> failing -> stopped -> player_exit -> entering_forest -> ending
        self.skipped: bool = False

        # Ground layout, shared between render() and the plant seeding below
        self.road_y: float = 170.0
        self.grass_strip_height: float = 50.0

        # Parallax tracking
        self.road_x: float = 0.0
        self.bg_far_x: float = 0.0
        self.bg_mid_x: float = 0.0
        self.bg_close_x: float = 0.0

        # Assets (loaded first to calibrate dimensions)
        self._load_intro_assets()

        # Vehicle
        car_w = self.car_surf.get_width()
        car_h = self.car_surf.get_height()
        self.car_x: float = 110.0
        self.car_y: float = 180.0 + (48.0 - car_h) / 2.0
        self.car_target_y: float = self.car_y
        self.car_shake: float = 0.0

        # The x where the player stops walking right and turns to face
        # north (see the player_exit arrival check below) always the
        # same number every playthrough, since neither car_x nor that
        # walk distance ever changes.
        self.forest_entry_x: float = self.car_x + car_w + 14.0

        # Roadside plants scroll in from the right on their own clock
        # same split Flappy Bird uses for its logs: a spawn timer decides
        # when a new one enters, and update() alone decides when an
        # existing one has scrolled off and gets dropped. Two rows, one
        # near the tree line and one near the road, each a back or front
        # layer of underbrush; PLANT_ROW_JITTER keeps every plant within
        # the same row instead of scattered across the whole strip.
        self.plant_row_y = [
            self.road_y - self.grass_strip_height - 25,
            self.road_y - 45.0,
        ]
        # A pre-seeded batch fills the screen right away with the same
        # spacing the timer would build up on its own (speed * interval),
        # so the drive-in doesn't open on an empty roadside while that
        # timer is still counting up to its first spawn.
        self.plants: List[RoadsidePlant] = []
        seed_spacing = max(1.0, self.speed * PLANT_SPAWN_INTERVAL)
        seed_x = 0.0
        while seed_x < settings.VIRTUAL_WIDTH:
            self._spawn_plant(seed_x)
            seed_x += seed_spacing
        self.plant_spawn_timer: float = 0.0

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

    def _remaining_scroll_distance(self) -> float:
        """
        How much further anything scrolling at ground speed still has to
        travel, from right now, before the car finishes coming to a full
        stop -- the "driving" phase runs at a constant speed for whatever
        is left of its fixed length, then "failing" brakes at a fixed
        rate down to 0. Both are deterministic, so this is exact, not a
        guess: it's what lets a plant spawned now know where it will
        actually end up once everything has settled.
        """
        if self.phase == "driving":
            remaining_driving = (DRIVING_PHASE_DURATION - self.time) * self.speed
            full_braking_distance = (self.speed ** 2) / (2.0 * CAR_DECELERATION)
            return remaining_driving + full_braking_distance
        if self.phase == "failing":
            return (self.speed ** 2) / (2.0 * CAR_DECELERATION)
        return 0.0

    def _spawn_plant(self, x: float) -> None:
        """
        Adds a plant at `x`, unless it's due to end up resting inside the
        reserved opening at forest_entry_x once the car finishes stopping
        -- in which case it's skipped outright rather than created and
        hidden later, so the gap is a real absence, not a render trick.
        """
        resting_x = x - self._remaining_scroll_distance()
        if abs(resting_x - self.forest_entry_x) <= FOREST_GAP_HALF_WIDTH:
            return

        row_y = random.choice(self.plant_row_y) + random.uniform(0, PLANT_ROW_JITTER)
        self.plants.append(RoadsidePlant(x, row_y, random.choice(self.plant_surfs)))

    def enter(self, *args, **kwargs) -> None:
        self.time = 0.0
        self.speed = 145.0
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
                if self.player_x >= self.car_x + self.car_surf.get_width() + 14:
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
            self.road_x = (self.road_x - self.speed * dt) % 64
            self.bg_far_x = (self.bg_far_x - self.speed * 0.12 * dt) % 592
            self.bg_mid_x = (self.bg_mid_x - self.speed * 0.28 * dt) % 592
            self.bg_close_x = (self.bg_close_x - self.speed * 0.5 * dt) % 592

            for plant in self.plants:
                plant.update(dt, self.speed)
            self.plants = [p for p in self.plants if not p.is_out_of_game()]

            self.plant_spawn_timer += dt
            if self.plant_spawn_timer >= PLANT_SPAWN_INTERVAL:
                self.plant_spawn_timer = 0.0
                self._spawn_plant(settings.VIRTUAL_WIDTH)

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

        # Forest backdrop, back to front. Each tree layer is taller than
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

        for tx in range(-64, settings.VIRTUAL_WIDTH + 64, 64):
            surface.blit(self.grass_tile, (tx + round(self.road_x), road_y - self.grass_strip_height))

        # Seamless road tiling
        for tx in range(-64, settings.VIRTUAL_WIDTH + 64, 64):
            surface.blit(self.road_tile, (tx + round(self.road_x), road_y))

        # Headlights beam (projecting forward onto dark road)
        if self.speed > 0.0 or self.phase in ("driving", "failing", "stopped", "player_exit"):
            light_beam = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            car_w = self.car_surf.get_width()
            car_h = self.car_surf.get_height()
            p_front = (self.car_x + car_w - 4, self.car_y + car_h // 2 + self.car_shake - 8)
            pygame.draw.polygon(
                light_beam,
                (255, 245, 180, 45),
                self._headlight_cone_points(p_front, 190, 26.6),
            )
            pygame.draw.polygon(
                light_beam,
                (255, 245, 180, 100),
                self._headlight_cone_points(p_front, 130, 21.7),
            )
            surface.blit(light_beam, (0, 0))

            light_beam2 = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            p_front2 = (self.car_x + car_w - 4, self.car_y + car_h // 2 + self.car_shake + 8)
            pygame.draw.polygon(
                light_beam2,
                (255, 245, 180, 45),
                self._headlight_cone_points(p_front2, 190, 26.6),
            )
            pygame.draw.polygon(
                light_beam2,
                (255, 245, 180, 100),
                self._headlight_cone_points(p_front2, 130, 21.7),
            )
            surface.blit(light_beam2, (0, 0))

        # Car vehicle
        surface.blit(self.car_surf, (round(self.car_x), round(self.car_y + self.car_shake)))

        # Roadside plants, scattered over the grass strip. Drawn back
        # row first so the front row overlaps it, reading as depth
        # instead of the two rows fighting for the same layer.
        for plant in sorted(self.plants, key=lambda p: p.y):
            plant.render(surface)

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

        # Smoke particles (from engine hood)
        self.smoke_particles.render(surface)

        # Ambient night darkness vignette
        darkness = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        darkness.fill((6, 8, 14, 130))
        surface.blit(darkness, (0, 0))

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