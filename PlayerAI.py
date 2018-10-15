from PythonClientAPI.game.PointUtils import *
from PythonClientAPI.game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.game.Enums import Team
from PythonClientAPI.game.World import World
from PythonClientAPI.game.TileUtils import TileUtils
from PythonClientAPI.game.PathFinder import *

class PlayerAI:

    def __init__(self):
        ''' Initialize! '''
        self.turn_count = 0             # game turn count
        self.target = None           # target to send unit to!
        self.outbound = True            # is the unit leaving, or returning?
        self.float_number = 0
        self.last_movement_direction = None

        self.first_square_safety = 0
        self.second_square_safety = 0
        self.first_square_safety_pos = None
        self.second_square_safety_pos = None

        self.current_square_being_closed = []
        self.closing_mode = False
        self.wall_stuck = 0
        self.last_turn_pos = None
        self.recently_wall_stuck = False


    def do_move(self, world, friendly_unit, enemy_units):
        '''
        This method is called every turn by the game engine.
        Make sure you call friendly_unit.move(target) somewhere here!

        Below, you'll find a very rudimentary strategy to get you started.
        Feel free to use, or delete any part of the provided code - Good luck!

        :param world: world object (more information on the documentation)
            - world: contains information about the game map.
            - world.path: contains various pathfinding helper methods.
            - world.util: contains various tile-finding helper methods.
            - world.fill: contains various flood-filling helper methods.

        :param friendly_unit: FriendlyUnit object
        :param enemy_units: list of EnemyUnit objects
        '''

        # increment turn count
        self.turn_count += 1

        #if I'm inside my own territory, I shouldnt be in closing mode, nor should I have queued up actions
        if friendly_unit.position in friendly_unit.territory:
            self.closing_mode = False
            self.current_square_being_closed = []
        #if its the first turn, you dont wanna run towards the wall for your first turn
        if self.turn_count < 2:
            self.target = world.path.get_shortest_path(friendly_unit.position,
                                                       world.util.get_closest_enemy_head_from(friendly_unit.position,
                                                        friendly_unit.snake).position,
                                                       friendly_unit.snake)[0]
            friendly_unit.move(self.target)
        elif self.closing_mode:
            #closing mode is when you're claiming the square thats being threatened
            #take off the first item in current_square_being_closed list, and move to that removed item
            if(len(self.current_square_being_closed) < 3):
                self.closing_mode = False
            current_square_holder = []
            for i in range(1, len(self.current_square_being_closed)):
                current_square_holder.append(self.current_square_being_closed[i])
            self.current_square_being_closed = current_square_holder
            next_point = self.current_square_being_closed[0]
            friendly_unit.move(world.path.get_next_point_in_shortest_path(friendly_unit.position, next_point))
        else:
            #if I'm already inside my own territory, run towards the closest thing thats capturable
            if friendly_unit.position in friendly_unit.territory:
                closest_capturable_tile = world.util.get_closest_capturable_territory_from(friendly_unit.position, [world.util.get_closest_enemy_head_from(friendly_unit.position, None)])
                next_step = world.path.get_shortest_path(friendly_unit.position, closest_capturable_tile.position, None)[0]
                for direction in world.get_neighbours(friendly_unit.position):
                    if world.get_neighbours(friendly_unit.position)[direction] == next_step:
                        self.last_movement_direction = direction
                friendly_unit.move(next_step)
            else:
                #build imaginary squares both sides
                snake_length = len(friendly_unit.snake)

                first_imaginary_square = []
                second_imaginary_square = []
                fixed_first = []
                fixed_second = []


                #if snake just got out of wallstuck, run back to own territory to reset
                if self.recently_wall_stuck:
                    self.recently_wall_stuck = False
                    self.closing_mode = True
                    self.wall_stuck = 0
                    self.current_square_being_closed.extend(
                        world.path.get_shortest_path(self.current_square_being_closed[-1],
                                                     world.util.get_closest_friendly_territory_from(
                                                         friendly_unit.position, friendly_unit.snake).position,
                                                     friendly_unit.snake))

                #if snake has been stuck in the same position for two turns, it is declared wallstuck and fixed
                if self.wall_stuck > 0:
                    self.closing_mode = True
                    self.current_square_being_closed = []
                    self.wall_stuck = 0
                    self.recently_wall_stuck = True
                    if self.last_movement_direction == Direction.WEST:
                        self.last_movement_direction = Direction.SOUTH
                        for i in range(1,4):
                            self.current_square_being_closed.append((friendly_unit.position[0],friendly_unit.position[1]+i))
                    elif self.last_movement_direction == Direction.NORTH:
                        self.last_movement_direction = Direction.WEST
                        for i in range(1,4):
                            self.current_square_being_closed.append((friendly_unit.position[0]-i,friendly_unit.position[1]))
                    elif self.last_movement_direction == Direction.EAST:
                        self.last_movement_direction == Direction.NORTH
                        for i in range(1,4):
                            self.current_square_being_closed.append((friendly_unit.position[0],friendly_unit.position[1]-i))
                    else:
                        self.last_movement_direction = Direction.EAST
                        for i in range(1,4):
                            self.current_square_being_closed.append((friendly_unit.position[0]+i,friendly_unit.position[1]))

                #build imaginary square to claim, depending on which direction the snake has been travelling
                if self.last_movement_direction == Direction.EAST:
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0], friendly_unit.position[1]-i))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]-i, friendly_unit.position[1]-snake_length))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]-snake_length, friendly_unit.position[1]-snake_length+i))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0], friendly_unit.position[1]+i))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]-i, friendly_unit.position[1]+snake_length))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]-snake_length, friendly_unit.position[1]+snake_length-i))
                elif self.last_movement_direction == Direction.WEST:
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0], friendly_unit.position[1]-i))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]+i, friendly_unit.position[1]-snake_length))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]+snake_length, friendly_unit.position[1]-snake_length+i))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0], friendly_unit.position[1]+i))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]+i, friendly_unit.position[1]+snake_length))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]+snake_length, friendly_unit.position[1]+snake_length-i))
                elif self.last_movement_direction == Direction.NORTH:
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]+i, friendly_unit.position[1]))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]+snake_length, friendly_unit.position[1]+i))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]+snake_length-i, friendly_unit.position[1]+snake_length))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]-i, friendly_unit.position[1]))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]-snake_length, friendly_unit.position[1]+i))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]-snake_length+i, friendly_unit.position[1]+snake_length))
                elif self.last_movement_direction == Direction.SOUTH:
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]+i, friendly_unit.position[1]))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]+snake_length, friendly_unit.position[1]-i))
                    for i in range(1,snake_length+1):
                        first_imaginary_square.append((friendly_unit.position[0]-i+snake_length, friendly_unit.position[1]-snake_length))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]-i, friendly_unit.position[1]))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]-snake_length, friendly_unit.position[1]-i))
                    for i in range(1,snake_length+1):
                        second_imaginary_square.append((friendly_unit.position[0]+i-snake_length, friendly_unit.position[1]-snake_length))

                #purge imaginary square of all out of bounds tuples, AND all wall tuples
                for first_tuple in first_imaginary_square:
                    if not(first_tuple[0] < 1 or first_tuple[0] > 28 or first_tuple[1] < 1 or first_tuple[1] > 28):
                        fixed_first.append(first_tuple)
                for second_tuple in second_imaginary_square:
                    if not(second_tuple[0] < 1 or second_tuple[0] > 28 or second_tuple[1] < 1 or second_tuple[1] > 28):
                        fixed_second.append(second_tuple)
                first_imaginary_square = fixed_first
                second_imaginary_square = fixed_second

                #walk perimeter of the imaginary squares until a safe point is found (worst case would be starting point)
                tile_map = world.position_to_tile_map

                self.first_square_safety = 0
                for first_square_perimeter_block in first_imaginary_square:
                    if not world.is_within_bounds(first_square_perimeter_block):
                        break
                    if tile_map[first_square_perimeter_block].is_friendly:
                        self.first_square_safety_pos = first_square_perimeter_block
                        break
                    else:
                        self.first_square_safety += 1

                self.second_square_safety = 0
                for second_square_perimeter_block in second_imaginary_square:
                    if not world.is_within_bounds(second_square_perimeter_block):
                        break
                    if tile_map[second_square_perimeter_block].is_friendly:
                        self.second_square_safety_pos = second_square_perimeter_block
                        break
                    else:
                        self.second_square_safety += 1

                #at each step and each larger imaginary square, check that no enemies are threatening the square
                first_square_threat_level = 999
                for first_square_perimeter_block in first_imaginary_square:
                    if not world.is_within_bounds(first_square_perimeter_block):
                        break
                    first_closest_threat_pos = world.util.get_closest_enemy_head_from(first_square_perimeter_block, friendly_unit.snake).position
                    dist_to_first_threat = world.path.get_shortest_path_distance(first_square_perimeter_block, first_closest_threat_pos)
                    if dist_to_first_threat > 0 and (dist_to_first_threat < first_square_threat_level):
                        first_square_threat_level = dist_to_first_threat

                second_square_threat_level = 999
                for second_square_perimeter_block in second_imaginary_square:
                    if not world.is_within_bounds(second_square_perimeter_block):
                        break
                    second_closest_threat_pos = world.util.get_closest_enemy_head_from(second_square_perimeter_block, friendly_unit.snake).position
                    dist_to_second_threat = world.path.get_shortest_path_distance(second_square_perimeter_block, second_closest_threat_pos)
                    if dist_to_second_threat > 0 and (dist_to_second_threat < second_square_threat_level):
                        second_square_threat_level = dist_to_second_threat

                #square_safety is the number of turns it would take to complete, and claim a square
                #threat_level is the number of turns it would take any enemy to destroy the imaginary square
                #if square_safety is greater than threat_level, claim the square
                if self.first_square_safety >= first_square_threat_level*1.5:
                    self.closing_mode = True
                    self.current_square_being_closed = first_imaginary_square
                    next_point = first_imaginary_square[0]
                    if world.path.get_next_point_in_shortest_path(friendly_unit.position, next_point) in friendly_unit.snake:
                        next_point = first_imaginary_square[1]
                        self.current_square_being_closed = first_imaginary_square[1:]
                    friendly_unit.move(world.path.get_next_point_in_shortest_path(friendly_unit.position, next_point))

                if self.second_square_safety >= second_square_threat_level*1.5:
                    self.closing_mode = True
                    self.current_square_being_closed = second_imaginary_square
                    next_point = second_imaginary_square[0]
                    if world.path.get_next_point_in_shortest_path(friendly_unit.position, next_point) in friendly_unit.snake:
                        next_point = second_imaginary_square[1]
                        self.current_square_being_closed = second_imaginary_square[1]
                    friendly_unit.move(world.path.get_next_point_in_shortest_path(friendly_unit.position, next_point))

                #increment wall_stuck if head hasn't moved
                if self.last_turn_pos == friendly_unit.position:
                    self.wall_stuck += 1
                self.last_turn_pos = friendly_unit.position
