"""
Base state class for all game states mounted on Gale StateStack.
"""

from typing import Any
import pygame
from gale.state import BaseState as GaleBaseState
from gale.input_handler import InputData


class BaseState(GaleBaseState):
    def __init__(self, state_stack: Any) -> None:
        super().__init__(state_stack)
        self.state_stack = state_stack

    def enter(self, *args: Any, **kwargs: Any) -> None:
        pass

    def exit(self) -> None:
        pass

    def on_input(self, input_id: str, input_data: InputData) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass
