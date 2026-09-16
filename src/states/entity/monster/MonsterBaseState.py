from typing import Tuple

import pygame
from gale.state import BaseState, StateMachine


class MonsterBaseState(BaseState):
    def __init__(self, monster, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.monster = monster

    def process_ai(self, house, player, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        self.monster.render_sprite(surface, camera_offset)
