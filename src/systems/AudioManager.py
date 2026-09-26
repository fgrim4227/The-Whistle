"""
Dynamic Audio System for 'El Silbón'.
Controls dedicated audio channels: continuous ambient background music,
periodic folklore whistling, panicked breathing, and composite dual jumpscares.
"""

import math
import random
from typing import Optional

import settings


class AudioManager:
    def __init__(self) -> None:
        self.ambient_tracks = ["ambience1", "ambience2"]
        self.current_ambient_idx = 0
        self.is_near_alert = False
        self.current_footstep_sound: Optional[str] = None
        
        # Cooldown timer for periodic whistling bursts (not continuous loops)
        self.whistle_cooldown = random.uniform(2.0, 6.0)
        self.thunder_timer = random.uniform(3.0, 6.0)
        self.bone_timer = random.uniform(1.0, 3.0)

        self.game_over_rain_delay = 1.5
        self.waiting_for_rain = False

    def start_ambient(self, track_name: Optional[str] = None) -> None:
        """Starts looping atmospheric cabin background music if not already playing."""
        ch = settings.AUDIO_CHANNELS.get("ambience")
        if ch and not ch.get_busy():
            track = track_name or self.ambient_tracks[self.current_ambient_idx]
            settings.play_music(track, loops=-1, volume=0.45, channel_name="ambience")

    def play_silbon_whistle(self, volume: float = 0.5) -> None:
        """Plays a single burst of the folklore whistle on its dedicated channel."""
        settings.play_sound("whistle", loops=0, volume=volume, channel_name="silbon_whistle")

    def update(
        self,
        player_center: tuple,
        monster_center: tuple,
        is_hidden: bool,
        monster_in_same_room: bool = True,
        door_listening_proximity: float = 0.0,
        dt: float = 0.016,
        monster_is_moving: bool = False,
        monster_ai_state: str = "patrol",
    ) -> None:
        """
        Modulates whistling volume, breathing, and footsteps in real-time:
        - Periodic Whistling: Plays periodically (every 14-24s) instead of an endless loop.
        - Folklore Paradox:
            * Farther real distance -> Louder perceived whistle (up to 0.85).
            * Closer real distance (< 80px) -> Faint whisper volume (down to 0.08).
        - Breathing: Audible when monster is close (< 150px), player is hidden, or player listens at a door.
        - Ambient Ducking: Lowers background ambience when listening closely to heavy breathing at a door.
        - Footsteps: Dynamic walk/run sounds when El Silbón stalks or chases the player.
        """
        dist = math.hypot(
            player_center[0] - monster_center[0],
            player_center[1] - monster_center[1]
        )
        max_range = 2000
        normalized = min(1.0, max(0.06, dist / max_range))

        # Modulate whistle volume inversely proportional to distance (baseline audibility >= 0.22)
        whistle_vol = max(0.1, normalized)

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
                    # Next whistle burst interval
                    self.whistle_cooldown = random.uniform(2.0, 6.0)

        # Proximity alert flag for UI
        self.is_near_alert = (dist < 100.0 and monster_in_same_room)

        # Ambient music volume ducking when listening closely at a door
        ch_amb = settings.AUDIO_CHANNELS.get("ambience")
        if ch_amb:
            if not ch_amb.get_busy():
                self.start_ambient()
            elif door_listening_proximity > 0.1:
                # Duck ambient volume from 0.45 down towards 0.15 for acoustic clarity
                ducked_vol = max(0.12, 0.45 * (1.0 - door_listening_proximity * 0.70))
                ch_amb.set_volume(ducked_vol)
            else:
                ch_amb.set_volume(0.45)

        # Panicked or door-listening breathing modulation
        ch_breath = settings.AUDIO_CHANNELS.get("silbon_breath")
        if ch_breath:
            if monster_in_same_room and (dist < 100):
                breath_vol = max(0.3, (1.0 - min(1.0, dist / 180.0)) * 0.90)
                if not ch_breath.get_busy():
                    settings.play_sound("breathing", loops=-1, volume=breath_vol, channel_name="silbon_breath")
                else:
                    ch_breath.set_volume(breath_vol)
            elif door_listening_proximity > 0.05:
                # Audible heavy breathing through wooden door
                breath_vol = max(0.8, min(0.95, door_listening_proximity * 0.95))
                if not ch_breath.get_busy():
                    settings.play_sound("breathing", loops=-1, volume=breath_vol, channel_name="silbon_breath")
                else:
                    ch_breath.set_volume(breath_vol)
            else:
                if ch_breath.get_busy():
                    settings.stop_channel("silbon_breath")

        # Footstep & running sounds for El Silbón
        ch_steps = settings.AUDIO_CHANNELS.get("silbon_footsteps")
        if ch_steps:
            should_play_steps = (
                monster_in_same_room
                and monster_is_moving
                and monster_ai_state not in ("stunned", "knocking")
                and dist < 260.0
            )
            if should_play_steps:
                target_sound = "run_sound" if monster_ai_state in ("chase", "berserk") else "walk_sound"
                step_vol = max(0.3, (1.0 - min(1.0, dist / 500)) * 0.85)

                if self.current_footstep_sound != target_sound or not ch_steps.get_busy():
                    settings.play_sound(target_sound, loops=-1, volume=step_vol, channel_name="silbon_footsteps")
                    self.current_footstep_sound = target_sound
                else:
                    ch_steps.set_volume(step_vol)
            else:
                if ch_steps.get_busy():
                    settings.stop_channel("silbon_footsteps")
                self.current_footstep_sound = None

    def start_title_audio(self) -> None:
        """Starts the title screen audio"""
        settings.stop_all_audio()
        amb_channel = settings.AUDIO_CHANNELS.get("ambience")
        if amb_channel and not amb_channel.get_busy():
            settings.play_music("ambience1", loops=-1, volume=0.2, channel_name="ambience")
        settings.play_sound("rain", loops=-1, volume=0.45, channel_name="title_weather")

    def update_title_audio(self, dt: float) -> bool:
        """Updates the title screen audio"""
        self.thunder_timer -= dt
        thunder_struck = False
        if self.thunder_timer <= 0:
            thunder_sound = random.choice(["thunder_1", "thunder_2", "thunder_3"])
            settings.play_sound(thunder_sound, volume=0.8, channel_name="thunder")
            self.thunder_timer = random.uniform(4.0, 10.0)
            thunder_struck = True
        amb_channel = settings.AUDIO_CHANNELS.get("ambience")
        if amb_channel and not amb_channel.get_busy():
            settings.play_music("ambience1", loops=-1, volume=0.2, channel_name="ambience")
            
        weather_channel = settings.AUDIO_CHANNELS.get("title_weather")
        if weather_channel and not weather_channel.get_busy():
             settings.play_sound("rain", loops=-1, volume=0.45, channel_name="title_weather")
        return thunder_struck

    def start_game_over_audio(self) -> None:
        """Starts the game over audio"""
        settings.stop_channel("ambience")
        settings.stop_channel("silbon_whistle")
        settings.stop_channel("silbon_breath")
        settings.stop_channel("silbon_footsteps")
        settings.stop_channel("thunder")
        
        settings.play_sound("jumpscare1", loops=0, volume=1.0, channel_name="jumpscare1")
        settings.play_sound("jumpscare2", loops=0, volume=1.0, channel_name="jumpscare2")
        self.game_over_rain_delay = 2.0
        self.waiting_for_rain = True

    def update_game_over_audio(self, dt: float, is_jumpscare_active: bool) -> None:
        """Updates the audio of the game over screen sounds"""
        if self.waiting_for_rain:
            self.game_over_rain_delay -= dt
            if self.game_over_rain_delay <= 0:
                self.waiting_for_rain = False
                weather_channel = settings.AUDIO_CHANNELS.get("title_weather")
                if weather_channel and not weather_channel.get_busy():
                    settings.play_sound("rain", loops=-1, volume=0.3, channel_name="title_weather")
                elif weather_channel:
                    weather_channel.set_volume(0.3)
                    
        if not is_jumpscare_active:
            self.bone_timer -= dt
            if self.bone_timer <= 0:
                bone_sfx = random.choice(["bone_snap_1", "bone_snap_2", "bone_snap_3", "bone_snap_4"])
                settings.play_sound(bone_sfx, volume=0.8, channel_name="bones")
                self.bone_timer = random.uniform(2.0, 4.0)