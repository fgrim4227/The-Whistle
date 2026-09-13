"""
Main game class ElSilbonGame based on gale.game.Game and gale.state.StateStack.
"""

import pygame
from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateStack

import settings
from src.states.game.StartState import StartState


class TheWhistle(Game):
    def init(self) -> None:
        self.state_stack = StateStack()
        # Game initializes into the StartState title screen
        self.state_stack.push(StartState(self.state_stack))

    def update(self, dt: float) -> None:
        self.state_stack.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_stack.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            # If in StartState, exit game; during gameplay, active states or PauseState handle quit
            if len(self.state_stack.states) == 1 and isinstance(self.state_stack.states[0], StartState):
                self.quit()
            else:
                self.state_stack.on_input(input_id, input_data)
        else:
            self.state_stack.on_input(input_id, input_data)
