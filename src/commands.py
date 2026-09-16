"""
Command classes for Andreas (bound to InputHandler through
CommandBindings in Player.__init__) and for El Silbón (his own states
call these same singletons directly from process_ai instead of a
hardcoded state-name string at every call site).

Movement and one-shot player commands only record intent on the
receiver (Player.held / Player.*_requested); resolving that intent
into actual movement or an interaction happens in Player's own states
and in PlayState.update(), never inside the command. Commands with no
further resolution step (flashlight/cycle_item/slot selection, and
El Silbón's transitions) just call the receiver's existing method
directly, since there is nothing left to decide afterwards.
"""

from gale.command import Command


class MoveLeftCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_left"] = True


class MoveRightCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_right"] = True


class MoveUpCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_up"] = True


class MoveDownCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_down"] = True


class StopMoveLeftCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_left"] = False


class StopMoveRightCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_right"] = False


class StopMoveUpCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_up"] = False


class StopMoveDownCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.held["move_down"] = False


class RunCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_running = True


class StopRunCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.is_running = False


class InteractCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.interact_requested = True


class ThrowCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.throw_requested = True


class DropCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.drop_requested = True


class FlashlightCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.toggle_flashlight()


class CycleItemCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.cycle_item()


class SelectSlot1Command(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.select_slot(0)


class SelectSlot2Command(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.select_slot(1)


class SelectSlot3Command(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.select_slot(2)


class SelectSlot4Command(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.select_slot(3)


class SelectSlot5Command(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.select_slot(4)


MOVE_LEFT = MoveLeftCommand()
MOVE_RIGHT = MoveRightCommand()
MOVE_UP = MoveUpCommand()
MOVE_DOWN = MoveDownCommand()
STOP_MOVE_LEFT = StopMoveLeftCommand()
STOP_MOVE_RIGHT = StopMoveRightCommand()
STOP_MOVE_UP = StopMoveUpCommand()
STOP_MOVE_DOWN = StopMoveDownCommand()
RUN = RunCommand()
STOP_RUN = StopRunCommand()
INTERACT = InteractCommand()
THROW = ThrowCommand()
DROP = DropCommand()
FLASHLIGHT = FlashlightCommand()
CYCLE_ITEM = CycleItemCommand()
SELECT_SLOT_1 = SelectSlot1Command()
SELECT_SLOT_2 = SelectSlot2Command()
SELECT_SLOT_3 = SelectSlot3Command()
SELECT_SLOT_4 = SelectSlot4Command()
SELECT_SLOT_5 = SelectSlot5Command()


# El Silbón's state-transition commands. Only the three transitions
# every state reaches with no extra data are covered here --
# moving_to_door/knocking/investigate/stunned all need door/target/
# duration kwargs Command.execute has no room for, so those stay as
# direct change_state(...) calls in the states that trigger them.
class ChaseCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.change_state("chase")


class PatrolCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.change_state("patrol")


class BerserkCommand(Command):
    def execute(self, receiver, dt: float = 0.0) -> None:
        receiver.change_state("berserk")


CHASE = ChaseCommand()
PATROL = PatrolCommand()
BERSERK = BerserkCommand()
