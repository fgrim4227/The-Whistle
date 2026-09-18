"""
Main game class ElSilbonGame based on gale.game.Game and gale.state.StateStack.
"""

import pygame
from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateStack
from gale.timer import Timer

import settings
from src.states.game.StartState import StartState
from src.states.game.WarningIntro import WarningIntro


class TheWhistle(Game):
    def __init__(self, *args, **kwargs) -> None:
        # Enable hardware-accelerated scaling, letterboxing, and the OS window maximize button
        kwargs.setdefault("flags", pygame.SCALED | pygame.RESIZABLE)
        super().__init__(*args, **kwargs)
        self.is_fullscreen: bool = False

    def init(self) -> None:
        # Set window titlebar and taskbar icon
        icon_path = settings.BASE_DIR / "assets" / "graphics" / "icon.png"
        if icon_path.exists():
            try:
                icon_surf = pygame.image.load(str(icon_path))
                pygame.display.set_icon(icon_surf)
            except Exception as e:
                print(f"Warning: Could not set window icon: {e}")

        self.state_stack = StateStack()
        # Game initializes into the content warning screen, which hands
        # off to the StartState title screen once it finishes
        self.state_stack.push(WarningIntro(self.state_stack))

    def update(self, dt: float) -> None:
        self.state_stack.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_stack.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "toggle_fullscreen" and input_data.pressed:
            pygame.display.toggle_fullscreen()
            self.is_fullscreen = not self.is_fullscreen
            return

        if input_id == "quit" and input_data.pressed:
            # If in StartState, exit game; during gameplay, active states or PauseState handle quit
            if len(self.state_stack.states) == 1 and isinstance(self.state_stack.states[0], StartState):
                self.quit()
            else:
                self.state_stack.on_input(input_id, input_data)
        else:
            self.state_stack.on_input(input_id, input_data)
