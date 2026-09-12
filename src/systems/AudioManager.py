"""
Dynamic Audio System for 'El Silbón'.
Controls dedicated audio channels: continuous ambient background music,
periodic folklore whistling, panicked breathing, door knock warnings, and composite dual jumpscares.
"""

import math
import random
from typing import Optional
import pygame

import settings


class AudioManager:
    def __init__(self) -> None:
        self.ambient_tracks = ["ambience1", "ambience2", "ambience3"]
        self.current_ambient_idx = 0
        self.is_near_alert = False
        
        # Cooldown timer for periodic whistling bursts (not continuous loops)
        self.whistle_cooldown = random.uniform(8.0, 15.0)

    def start_ambient(self, track_name: Optional[str] = None) -> None:
        """Starts looping atmospheric cabin background music if not already playing."""
        ch = settings.AUDIO_CHANNELS.get("ambience")
        if ch and not ch.get_busy():
            track = track_name or self.ambient_tracks[self.current_ambient_idx]
            settings.play_music(track, loops=-1, volume=0.45, channel_name="ambience")

    def play_silbon_whistle(self, volume: float = 0.5) -> None:
        """Plays a single burst of the folklore whistle on its dedicated channel."""
        settings.play_sound("whistle", loops=0, volume=volume, channel_name="silbon_whistle")

    def stop_silbon_whistle(self) -> None:
        """Stops whistling playback."""
        settings.stop_channel("silbon_whistle")

    def play_knock_door(self) -> None:
        """Plays the door knock sound effect before the monster bursts in."""
        settings.play_sound("knock_door", loops=0, volume=1.0, channel_name="knock")

    def play_composite_jumpscare(self) -> None:
        """
        Plays both jumpscare effects (jumpscare1 and jumpscare2) simultaneously
        while silencing other background channels for maximum terror impact.
        """
        settings.stop_channel("ambience")
        settings.stop_channel("silbon_whistle")
        settings.stop_channel("silbon_breath")
        
        settings.play_sound("jumpscare1", loops=0, volume=1.0, channel_name="jumpscare1")
        settings.play_sound("jumpscare2", loops=0, volume=1.0, channel_name="jumpscare2")

    def update(
        self,
        player_center: tuple,
        monster_center: tuple,
        is_hidden: bool,
        monster_in_same_room: bool = True,
        dt: float = 0.016,
    ) -> None:
        """
        Modulates whistling volume and breathing in real-time:
        - Periodic Whistling: Plays periodically (every 14-24s) instead of an endless loop.
        - Folklore Paradox:
            * Farther real distance -> Louder perceived whistle (up to 0.85).
            * Closer real distance (< 80px) -> Faint whisper volume (down to 0.08).
        - Breathing: Audible and panicking when the monster is very close (< 140px) or player hides.
        """
        dist = math.hypot(
            player_center[0] - monster_center[0],
            player_center[1] - monster_center[1]
        )

        max_range = 380.0
        normalized = min(1.0, max(0.0, dist / max_range))

        # Modulate whistle volume inversely proportional to distance
        whistle_vol = max(0.08, normalized * 0.85)

        ch_whistle = settings.AUDIO_CHANNELS.get("silbon_whistle")
        if ch_whistle:
            if ch_whistle.get_busy():
                # If whistle is currently playing, adjust its volume dynamically
                ch_whistle.set_volume(whistle_vol)
            else:
                # Count down cooldown towards next whistle burst
                self.whistle_cooldown -= dt
                if self.whistle_cooldown <= 0.0:
                    self.play_silbon_whistle(volume=whistle_vol)
                    # Next whistle burst interval (14 to 24s silence)
                    self.whistle_cooldown = random.uniform(14.0, 24.0)

        # Proximity alert flag for UI
        self.is_near_alert = (dist < 100.0 and monster_in_same_room)

        # Panicked breathing modulation
        ch_breath = settings.AUDIO_CHANNELS.get("silbon_breath")
        if ch_breath:
            if monster_in_same_room and (dist < 150.0 or is_hidden):
                breath_vol = max(0.2, (1.0 - min(1.0, dist / 180.0)) * 0.90)
                if not ch_breath.get_busy():
                    settings.play_sound("breathing", loops=-1, volume=breath_vol, channel_name="silbon_breath")
                else:
                    ch_breath.set_volume(breath_vol)
            else:
                if ch_breath.get_busy():
                    settings.stop_channel("silbon_breath")
