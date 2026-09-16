from gale.state import BaseState, StateMachine


class PlayerBaseState(BaseState):
    def __init__(self, player, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.player = player
