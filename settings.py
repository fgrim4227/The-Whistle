"""
El Silbón: Nightmare at the Cabin (2D Survival Horror)
Global configurations, constants, input mappings, audio channels, and resource paths.
"""

import pathlib
import pygame

from gale import frames
from gale import input_handler

# Keyboard action bindings
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_p, "pause")

# Movement: Arrows and WASD
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "move_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_w, "move_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "move_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_s, "move_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LSHIFT, "run")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RSHIFT, "run")

# Survival actions
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_e, "interact")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_f, "flashlight")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_q, "throw")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "action")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_TAB, "objectives")

# Inventory management
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_c, "cycle_item")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_1, "slot_1")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_2, "slot_2")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_3, "slot_3")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_4, "slot_4")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_5, "slot_5")

# Menu navigation
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_l, "toggle_language")

TITLE = "El Silbon"

# Language configuration boolean: False = Spanish (default), True = English
IS_ENGLISH: bool = False

BASE_DIR = pathlib.Path(__file__).parent

# Virtual Resolution: Exact 16:9 ratio with 32x32 tiles (16 cols x 9 rows)
VIRTUAL_WIDTH = 512
VIRTUAL_HEIGHT = 288

# Actual window resolution (uniform 2.5x scale)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

TILE_SIZE = 32
GRID_COLS = VIRTUAL_WIDTH // TILE_SIZE  # 16
GRID_ROWS = VIRTUAL_HEIGHT // TILE_SIZE  # 9

# Gameplay and survival parameters
PLAYER_SPEED = 69  # px/s
PLAYER_RUN_SPEED = 75  # px/s
MONSTER_PATROL_SPEED = 70.0  # px/s
MONSTER_CHASE_SPEED = 105.0  # px/s
MONSTER_BERSERK_SPEED = 300  # px/s (+80% speed when enraged)

BATTERY_DRAIN_RATE = 0.9  # Percentage per second while flashlight is ON
BATTERY_RECHARGE_AMOUNT = 35.0  # Battery refill per picked-up battery item

# Throw probabilities
THROW_STUN_CHANCE = 0.8  # 75% chance to stun the monster
THROW_BERSERK_CHANCE = 0.2  # 25% chance to enrage the monster

# Global color definitions (RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_RED = (140, 20, 20)
COLOR_BLOOD_RED = (180, 0, 0)
COLOR_SILBON_RED = (184, 2, 0)  # Hex #b80200 from jumpscare artwork
COLOR_GOLD = (230, 190, 40)
COLOR_GRAY = (120, 120, 130)
COLOR_DARK_BLUE = (12, 12, 22)
COLOR_FLASHLIGHT = (255, 250, 220)
COLOR_MONSTER_EYES = (255, 25, 20)

# Light radii (world px), tunable here for quick testing without touching
# LightingSystem itself.
FLASHLIGHT_LIGHT_RADIUS = 92.0
MONSTER_EYE_LIGHT_RADIUS = 64.0

# Default fonts using SysFont fallback
pygame.font.init()
FONTS = {
    "small": pygame.font.SysFont("arial", 13, bold=True),
    "hud": pygame.font.SysFont("arial", 12, bold=True),
    "medium": pygame.font.SysFont("arial", 16, bold=True),
    "large": pygame.font.SysFont("arial", 24, bold=True),
    "title": pygame.font.SysFont("georgia", 36, bold=True),
    "note_title": pygame.font.SysFont("georgia", 15, bold=True),
    "note_body": pygame.font.SysFont("georgia", 12),
    "dialogue": pygame.font.SysFont("arial", 13, bold=True),
}

# Initialize audio system with 16 dedicated mixer channels
try:
    if pygame.mixer.get_init() is None:
        pygame.mixer.init()
    pygame.mixer.set_num_channels(16)
except Exception as e:
    print(f"Warning: could not initialize pygame.mixer ({e})")

# Sound dictionary
SOUNDS = {
    "whistle": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "whistle.mp3"),
    "breathing": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "breathing.wav"),
    "walk_sound": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "walk_sound.mp3"),
    "run_sound": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "run_sound.mp3"),
    "ambience1": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "ambient" / "ambience1.mp3"),
    "ambience2": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "ambient" / "ambience2.mp3"),
    "ambience3": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "ambient" / "ambience3.mp3"),
    "knock_door": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "knock_door.mp3"),
    "jumpscare1": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "jumpscare1.mp3"),
    "jumpscare2": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "jumpscare2.mp3"),
    "jumpscare3": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "screams.wav"),
    "minigame_lock_forced": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "minigames" / "lock_forced.mp3"),
    "minigame_normal_click": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "minigames" / "normal_click.wav"),
    "minigame_unlock_click": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "minigames" / "unlock_click.mp3"),
    "minigame_wood_break": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "sfx" / "minigames" / "wood_break.mp3"),
}
# Dedicated Audio Channels (Ultimate Fantasy architecture pattern)
AUDIO_CHANNELS = {
    "ambience": pygame.mixer.Channel(0) if pygame.mixer.get_init() else None,
    "silbon_whistle": pygame.mixer.Channel(1) if pygame.mixer.get_init() else None,
    "silbon_breath": pygame.mixer.Channel(2) if pygame.mixer.get_init() else None,
    "knock": pygame.mixer.Channel(3) if pygame.mixer.get_init() else None,
    "jumpscare1": pygame.mixer.Channel(4) if pygame.mixer.get_init() else None,
    "jumpscare2": pygame.mixer.Channel(5) if pygame.mixer.get_init() else None,
    "sfx": pygame.mixer.Channel(6) if pygame.mixer.get_init() else None,
    "silbon_footsteps": pygame.mixer.Channel(7) if pygame.mixer.get_init() else None,
    "minigame": pygame.mixer.Channel(8) if pygame.mixer.get_init() else None,
}

def play_sound(name: str, loops: int = 0, volume: float = 1.0, channel_name: str = None):
    """Plays a sound clip with specified volume and optional dedicated channel."""
    sound = SOUNDS.get(name)
    if sound is None:
        return None
    sound.set_volume(volume)
    if channel_name and AUDIO_CHANNELS.get(channel_name):
        channel = AUDIO_CHANNELS[channel_name]
        channel.play(sound, loops=loops)
        return channel
    return sound.play(loops=loops)

def play_music(name: str, loops: int = -1, volume: float = 0.5, channel_name: str = "ambience"):
    """Plays background ambient music on loop."""
    return play_sound(name, loops=loops, volume=volume, channel_name=channel_name)

def stop_channel(channel_name: str):
    """Stops audio playback on the specified channel."""
    channel = AUDIO_CHANNELS.get(channel_name)
    if channel is not None:
        channel.stop()

def set_channel_volume(channel_name: str, volume: float):
    """Updates the volume of a specific audio channel in real-time."""
    channel = AUDIO_CHANNELS.get(channel_name)
    if channel is not None:
        channel.set_volume(volume)

def stop_all_audio():
    """Stops playback on all active audio channels."""
    for channel in AUDIO_CHANNELS.values():
        if channel is not None:
            channel.stop()

# Texture dictionary
TEXTURES = {
    # Player sprites (Andreas)
    "player_walk_down": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "player" / "Andreas" / "andreas walk down.png"
    ),
    "player_walk_up": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "player" / "Andreas" / "Andreas walk back.png"
    ),
    "player_walk_left": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "player" / "Andreas" / "andreas left walk.png"
    ),
    "player_walk_right": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "player" / "Andreas" / "andreas right side walk.png"
    ),
    "player_idle": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "player" / "Andreas" / "andreas idle animation.png"
    ),
    "player_dying": pygame.image.load(
        BASE_DIR / "assets" / "graphics" / "characters" / "player" / "Andreas" / "Andreas dying.png"
    ),

    # Monster sprites (El Silbón)
    "monster_idle": pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "monster" / "monster_idle.png"),
    "monster_walk": pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "monster" / "monster_walk.png"),
    "monster_running": pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "monster" / "monster_running.png"),

    # Jumpscare textures
    "silbon_attack": pygame.image.load(BASE_DIR / "assets" / "graphics" / "jumpscare" / "silbon_attack.png"),
    "silbon_sad": pygame.image.load(BASE_DIR / "assets" / "graphics" / "jumpscare" / "silbon_sad.png"),
    "silbon_red": pygame.image.load(BASE_DIR / "assets" / "graphics" / "jumpscare" / "silbon_red.png"),
}

# Animation frame rects, sliced once per texture and indexed 1-based by
# src.definitions.entity's animation specs via frame() below.
FRAMES = {
    "player_walk_down": frames.generate_frames(TEXTURES["player_walk_down"], 16, 32),
    "player_walk_up": frames.generate_frames(TEXTURES["player_walk_up"], 16, 32),
    "player_walk_left": frames.generate_frames(TEXTURES["player_walk_left"], 16, 32),
    "player_walk_right": frames.generate_frames(TEXTURES["player_walk_right"], 16, 32),
    "player_idle": frames.generate_frames(TEXTURES["player_idle"], 16, 32),
    "player_dying": frames.generate_frames(TEXTURES["player_dying"], 16, 32),
    "monster_idle": frames.generate_frames(TEXTURES["monster_idle"], 64, 64),
    "monster_walk": frames.generate_frames(TEXTURES["monster_walk"], 92, 92),
    "monster_running":frames.generate_frames(TEXTURES["monster_running"], 92, 92),
}


def frame(texture_id: str, one_based_index: int) -> pygame.Rect:
    return FRAMES[texture_id][one_based_index - 1]
