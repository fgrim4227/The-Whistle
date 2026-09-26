"""
TitleWhistlerEffect: Handles FNAF-style erratic twitching, shifting, and looming
zoom surges for El Silbón on the main menu title screen.
"""

import random
from typing import Dict, List, Optional, Tuple

import pygame
import settings


class TitleWhistlerEffect:
    """
    Manages the animated horror presentation of El Silbón in StartState.
    Pre-scales all directional and glitch frames into two cached tiers
    (Distant and Looming) to guarantee zero runtime scaling overhead and 60 FPS.
    """

    def __init__(self) -> None:
        self.title_dir = settings.BASE_DIR / "assets" / "graphics" / "title"

        self.screen_w = settings.VIRTUAL_WIDTH
        self.screen_h = settings.VIRTUAL_HEIGHT

        # Tier 1: Distant / Normal dimensions
        self.distant_size = (self.screen_w, self.screen_h)

        # Tier 2: Looming / Close-up dimensions (+25% scale, centered with negative offset)
        self.looming_scale = 1.25
        self.looming_w = int(self.screen_w * self.looming_scale)
        self.looming_h = int(self.screen_h * self.looming_scale)
        self.looming_size = (self.looming_w, self.looming_h)
        self.base_looming_offset = (
            (self.screen_w - self.looming_w) // 2,
            (self.screen_h - self.looming_h) // 2,
        )

        # Frame collections
        self.distant_frames: Dict[str, pygame.Surface] = {}
        self.looming_frames: Dict[str, pygame.Surface] = {}

        self.frame_names: List[str] = [
            "titlescreen.png",
            "left.png",
            "right.png",
            "down.png",
            "Sprite-0005.png",
            "Sprite-0006.png",
            "Sprite-0007.png",
            "Sprite-0008.png",
        ]

        self.distant_twitch_keys: List[str] = [
            "left.png",
            "right.png",
            "down.png",
            "Sprite-0005.png",
            "titlescreen.png",
        ]

        self.looming_twitch_keys: List[str] = [
            "Sprite-0005.png",
            "Sprite-0006.png",
            "Sprite-0007.png",
            "Sprite-0008.png",
            "left.png",
            "right.png",
            "down.png",
            "titlescreen.png",
        ]

        # Load and pre-scale all surfaces
        self._load_and_cache_frames()

        # State management
        # States: "idle", "twitch_distant", "looming_surge"
        self.state = "idle"
        self.state_timer = random.uniform(2.0, 4.2)
        self.jitter_timer = 0.0
        self.current_surface: Optional[pygame.Surface] = self.distant_frames.get("titlescreen.png")
        self.current_offset: Tuple[int, int] = (0, 0)

    def _load_and_cache_frames(self) -> None:
        """Loads and pre-scales all PNG variations once into memory."""
        for name in self.frame_names:
            file_path = self.title_dir / name
            if not file_path.exists():
                continue
            try:
                raw_surf = pygame.image.load(str(file_path)).convert_alpha()
                s_distant = pygame.transform.scale(raw_surf, self.distant_size)
                s_looming = pygame.transform.scale(raw_surf, self.looming_size)
                self.distant_frames[name] = s_distant
                self.looming_frames[name] = s_looming
            except Exception as e:
                print(f"Warning: Could not load title frame '{name}': {e}")

        # Fallback if titlescreen.png is missing
        if "titlescreen.png" not in self.distant_frames:
            fallback = pygame.Surface(self.distant_size)
            fallback.fill(settings.COLOR_DARK_BLUE)
            self.distant_frames["titlescreen.png"] = fallback
            self.looming_frames["titlescreen.png"] = fallback

    def trigger_surge(self) -> None:
        """Forces an immediate close-up surge (e.g. synchronized with lightning/thunder)."""
        self.state = "looming_surge"
        self.state_timer = random.uniform(0.35, 0.55)
        self.jitter_timer = 0.0
        self._pick_looming_frame()

    def update(self, dt: float) -> None:
        """Updates twitch timers and frame transitions."""
        if self.state == "idle":
            self.current_surface = self.distant_frames.get("titlescreen.png")
            self.current_offset = (0, 0)
            self.state_timer -= dt
            if self.state_timer <= 0.0:
                # Roll for distant twitch vs aggressive looming surge
                if random.random() < 0.72:
                    self.state = "twitch_distant"
                    self.state_timer = random.uniform(0.18, 0.32)
                else:
                    self.state = "looming_surge"
                    self.state_timer = random.uniform(0.32, 0.50)
                self.jitter_timer = 0.0

        elif self.state == "twitch_distant":
            self.state_timer -= dt
            self.jitter_timer -= dt
            if self.jitter_timer <= 0.0:
                self.jitter_timer = random.uniform(0.04, 0.07)
                key = random.choice(self.distant_twitch_keys)
                self.current_surface = self.distant_frames.get(key, self.distant_frames["titlescreen.png"])
                # Slight micro jitter
                jx = random.choice([-2, 0, 2])
                jy = random.choice([-1, 0, 1])
                self.current_offset = (jx, jy)

            if self.state_timer <= 0.0:
                self.state = "idle"
                self.state_timer = random.uniform(2.2, 4.5)
                self.current_surface = self.distant_frames["titlescreen.png"]
                self.current_offset = (0, 0)

        elif self.state == "looming_surge":
            self.state_timer -= dt
            self.jitter_timer -= dt
            if self.jitter_timer <= 0.0:
                self.jitter_timer = random.uniform(0.035, 0.055)
                self._pick_looming_frame()

            if self.state_timer <= 0.0:
                self.state = "idle"
                self.state_timer = random.uniform(2.5, 5.0)
                self.current_surface = self.distant_frames["titlescreen.png"]
                self.current_offset = (0, 0)

    def _pick_looming_frame(self) -> None:
        """Picks a random erratic frame from the zoomed looming collection."""
        key = random.choice(self.looming_twitch_keys)
        self.current_surface = self.looming_frames.get(key, self.looming_frames["titlescreen.png"])
        # Micro vibration around the centered looming position
        jx = random.randint(-4, 4)
        jy = random.randint(-3, 3)
        self.current_offset = (
            self.base_looming_offset[0] + jx,
            self.base_looming_offset[1] + jy,
        )

    def render(self, surface: pygame.Surface) -> None:
        """Renders the current frame at its active jitter offset."""
        if self.current_surface:
            surface.blit(self.current_surface, self.current_offset)
