"""
Intro cutscene state (IntroRoadState).
Procedurally animated parallax drive along Carretera Trasandina (Mérida - Barinas),
featuring Gale ParticleSystem smoke, engine failure, Andreas exit, and El Silbón ambush.
"""

import math
import os
import random
from typing import List, Optional, Tuple
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
        self.phase: str = "driving"  # driving -> failing -> stopped -> player_exit -> ambush -> black
        self.skipped: bool = False

        # Parallax tracking
        self.road_x: float = 0.0
        self.bg_far_x: float = 0.0
        self.bg_mid_x: float = 0.0
        self.plant_spawn_timer: float = 0.0
        self.plants: List[RoadsidePlant] = []

        # Assets (loaded first to calibrate dimensions)
        self._load_intro_assets()

        # Vehicle
        car_w = self.car_surf.get_width()
        car_h = self.car_surf.get_height()
        self.car_x: float = 110.0
        self.car_y: float = 120.0 + (48.0 - car_h) / 2.0
        self.car_target_y: float = self.car_y
        self.car_shake: float = 0.0

        # Player (Andreas)
        self.andreas_x: float = 0.0
        self.andreas_y: float = 0.0
        self.andreas_active: bool = False
        self.andreas_walking: bool = False

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
        road_path = os.path.join(intro_dir, "roads2W.png")
        car_path = os.path.join(intro_dir, "car_082.png")
        if not os.path.exists(car_path):
            car_path = os.path.join(intro_dir, "car.png")

        # Road tile
        if os.path.exists(road_path):
            sheet = pygame.image.load(road_path)
            self.road_tile = sheet.subsurface(pygame.Rect(128, 0, 64, 48))
        else:
            self.road_tile = pygame.Surface((64, 48))
            self.road_tile.fill((60, 60, 65))

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

        # Plants
        self.plant_surfs = []
        for i in range(1, 6):
            p_path = os.path.join(intro_dir, f"Plant{i}.png")
            if os.path.exists(p_path):
                self.plant_surfs.append(pygame.image.load(p_path))

        # Initial seed of roadside plants
        if self.plant_surfs:
            for x in [30, 110, 200, 290, 370, 460]:
                self.plants.append(RoadsidePlant(x, 62, random.choice(self.plant_surfs)))
                self.plants.append(RoadsidePlant(x + 40, 160, random.choice(self.plant_surfs)))

        # Player walk animations
        self.player_animations, self.player_textures = entity_defs.build_animations(
            entity_defs.PLAYER_ANIMATIONS, entity_defs.PLAYER_FALLBACK_COLOR, entity_defs.PLAYER_SIZE
        )
        self.current_anim = self.player_animations.get("walk-right")
        self.current_anim_key = "player_walk_right"

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
                # Stop car sounds: Andreas turns off the vehicle before stepping out
                settings.stop_channel("vehicle")
                self.andreas_active = True
                self.andreas_x = self.car_x + 35
                self.andreas_y = self.car_y + self.car_surf.get_height() - 4
                self.andreas_walking = True
                self.sub_text = "Maldición... el radiador hirvió. No hay señal aquí." if not settings.IS_ENGLISH else "Damn it... radiator boiled over. No phone signal out here."

        elif self.phase == "player_exit":
            if self.andreas_walking:
                self.andreas_x += 16.0 * dt
                if self.andreas_x >= self.car_x + self.car_surf.get_width() + 14:
                    self.andreas_walking = False
                    self.current_anim = self.player_animations.get("idle-right")
                    self.current_anim_key = "player_idle"
                    self.time_ambush_wait = self.time
                    # Andreas pauses in the dark silence by the roadside
                    self.sub_text = "¿Quién anda ahí...? ¿Hay alguien?" if not settings.IS_ENGLISH else "Who's out there...? Anyone around?"

            elif hasattr(self, "time_ambush_wait") and (self.time - self.time_ambush_wait >= 2.5):
                self.phase = "ambush"
                self.time_ambush = self.time
                # Jumpscare attack
                settings.play_sound("jumpscare1", volume=0.85, channel_name="jumpscare1")
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

        # Update Andreas animation
        if self.andreas_active and self.current_anim:
            self.current_anim.update(dt)

        # Update Parallax scrolling (only when speed > 0)
        if self.speed > 0.0:
            self.road_x = (self.road_x - self.speed * dt) % 64
            self.bg_far_x = (self.bg_far_x - self.speed * 0.12 * dt) % 512
            self.bg_mid_x = (self.bg_mid_x - self.speed * 0.28 * dt) % 512

            for plant in self.plants:
                plant.update(dt, self.speed)
            self.plants = [p for p in self.plants if p.x > -70]

            # Procedural plant spawner
            self.plant_spawn_timer += dt
            if self.plant_spawn_timer >= random.uniform(0.55, 1.15):
                self.plant_spawn_timer = 0.0
                if self.plant_surfs:
                    p_img = random.choice(self.plant_surfs)
                    # Alternate between top and bottom roadside
                    py = 62 if random.random() < 0.5 else 160
                    self.plants.append(RoadsidePlant(520, py, p_img))

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

        # 1. Midnight sky & mountains
        surface.fill((6, 10, 18))
        for x in range(-70, 580, 70):
            mx = x + round(self.bg_far_x % 70)
            pygame.draw.polygon(surface, (12, 18, 28), [(mx, 100), (mx + 45, 45), (mx + 90, 100)])
        for x in range(-50, 560, 50):
            mx = x + round(self.bg_mid_x % 50)
            pygame.draw.polygon(surface, (18, 24, 35), [(mx, 110), (mx + 35, 65), (mx + 70, 110)])

        # 2. Road & Grass
        road_y = 120
        pygame.draw.rect(surface, (160, 192, 112), (0, road_y - 30, settings.VIRTUAL_WIDTH, 110))

        # Seamless road tiling
        for tx in range(-64, settings.VIRTUAL_WIDTH + 64, 64):
            surface.blit(self.road_tile, (tx + round(self.road_x), road_y))

        # 3. Top roadside plants (behind car)
        for plant in self.plants:
            if plant.y < road_y:
                plant.render(surface)

        # 4. Headlights beam (projecting forward onto dark road)
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

        # 5. Car vehicle
        surface.blit(self.car_surf, (round(self.car_x), round(self.car_y + self.car_shake)))

        # 6. Andreas player sprite (if stepped out)
        if self.andreas_active and self.current_anim:
            frame = self.current_anim.get_current_frame()
            tex = settings.TEXTURES.get(self.current_anim_key)
            if tex and isinstance(frame, pygame.Rect):
                surface.blit(tex, (round(self.andreas_x), round(self.andreas_y)), frame)
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (round(self.andreas_x), round(self.andreas_y)))
            else:
                pygame.draw.rect(surface, entity_defs.PLAYER_FALLBACK_COLOR, (round(self.andreas_x), round(self.andreas_y), 16, 32))

        # 7. Smoke particles (from engine hood)
        self.smoke_particles.render(surface)

        # 8. Bottom roadside plants (in front of car/road)
        for plant in self.plants:
            if plant.y >= road_y:
                plant.render(surface)

        # 9. Ambient night darkness vignette
        darkness = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        darkness.fill((6, 8, 14, 130))
        surface.blit(darkness, (0, 0))

        # Jumpscare flash during ambush
        if self.phase == "ambush":
            flash = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            flash.fill((180, 0, 0, 190))
            surface.blit(flash, (0, 0))

        # 10. Subtitles & HUD skip prompt
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
