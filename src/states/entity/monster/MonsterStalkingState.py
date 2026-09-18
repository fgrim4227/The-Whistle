import math

import settings
from src.commands import CHASE, PATROL
from src.states.entity.monster.MonsterBaseState import MonsterBaseState
from src.systems import Pathfinding

CONFIRM_DETECTION_TIME = 2.5

LOST_TRAIL_TIMEOUT = 6.0

WAYPOINT_ARRIVAL_DIST = 10.0

LISTEN_SOUND_INTERVAL = 1.8

# How far the player has to actually move before the route to them gets
# recalculated. Sustained detection (the flashlight makes this common,
# tripling view distance) would otherwise re-plan on every single frame
# even while the player stands still, and a freshly re-planned route can
# start off in a slightly different direction than the one it replaces --
# showing up as the monster rocking between two positions instead of
# committing to a path.
REPATH_DIST = 32.0


class MonsterStalkingState(MonsterBaseState):

    """
    It knows roughly where the player was the last time
    it truly detected them, and walks slowly to that spot 
    to check—but it only escalates to a full-blown chase 
    if the detection persists or the player does something
     to give themselves away (like running nearby)
    """
    def enter(self, target_x: float, target_y: float, *args, **kwargs) -> None:
        self.monster.speed = settings.MONSTER_PATROL_SPEED
        self.time_since_detection = 0.0
        self.confirm_timer = 0.0
        self.listen_timer = 0.0
        self.target_x = target_x
        self.target_y = target_y
        self.path = []
        self.path_index = 0
        self.needs_path = True
        self.monster.change_animation(f"walk-{self.monster.direction}")

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"

        if self.monster.current_room_name != player_room_name:
            #Player changed of room so the monster lost his trail, go back to patrol
            PATROL(self.monster)
            return

        current_room = house.rooms.get(self.monster.current_room_name)
        if not current_room:
            PATROL(self.monster)
            return

        if not player.is_hidden and self.monster.can_detect_player(player, house):

            new_target_x, new_target_y = player.get_center()
            if math.hypot(new_target_x - self.target_x, new_target_y - self.target_y) > REPATH_DIST:
                self.needs_path = True
            self.target_x, self.target_y = new_target_x, new_target_y
            self.time_since_detection = 0.0
            self.listen_timer = 0.0
            self.confirm_timer += dt

            sustained_detection = self.confirm_timer >= CONFIRM_DETECTION_TIME
            gave_away_by_running = player.is_running and self.monster.distance_to_player <= 160.0
            if sustained_detection or gave_away_by_running:
                CHASE(self.monster)
                return
        else:
            self.confirm_timer = 0.0
            self.time_since_detection += dt
            if self.time_since_detection >= LOST_TRAIL_TIMEOUT:
                PATROL(self.monster)
                return

        if self.needs_path:
            route_width, min_route_width = self.monster.get_route_widths()
            self.path = Pathfinding.find_path(
                current_room, self.monster.get_collision_center(), (self.target_x, self.target_y),
                entity_width=route_width, min_entity_width=min_route_width
            )
            self.path_index = 0
            self.needs_path = False

        if not self.path:
            # An empty path means find_path() never found a route to the
            # target at all -- not that we walked one and finished. Push
            # straight toward the target instead of standing still.
            obstacles = current_room.get_obstacles()
            self.monster.move_towards(self.target_x, self.target_y, obstacles, dt)
            return

        if self.path_index >= len(self.path):
            # Monster arrives at the target position and listens for more clues
            self.monster.vx = 0.0
            self.monster.vy = 0.0
            self.monster.is_moving = False
            self.monster.change_animation("idle")

            self.listen_timer += dt
            if self.listen_timer >= LISTEN_SOUND_INTERVAL:
                self.listen_timer = 0.0
                settings.play_sound("breathing", volume=0.6, channel_name="silbon_breath")

            return

        wp_x, wp_y = self.path[self.path_index]
        obstacles = current_room.get_obstacles()
        self.monster.move_towards(wp_x, wp_y, obstacles, dt)

        mx, my = self.monster.get_collision_center()
        if math.hypot(wp_x - mx, wp_y - my) < WAYPOINT_ARRIVAL_DIST:
            self.path_index += 1