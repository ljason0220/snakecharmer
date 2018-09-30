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
        self.threat_turns = None
        self.safety_turns = None
        self.float_number = 0


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

        #if its the first turn, you obviously dont wanna run towards the wall first thing
        if self.turn_count == 1:
            self.target = world.path.get_shortest_path(friendly_unit.position,
                        world.util.get_closest_enemy_head_from(friendly_unit.position, friendly_unit.snake).position,
                        friendly_unit.snake)[0]
            print(friendly_unit.position)
            print(self.target)
            friendly_unit.move(self.target)

        #calculate current threat
        for body_chunk in friendly_unit.snake:
            chunk_threat = world.path.get_shortest_path_distance(body_chunk,
                        world.util.get_closest_enemy_head_from(body_chunk, friendly_unit.snake).position)
            if self.threat_turns == None or chunk_threat < self.threat_turns:
                self.threat_turns = chunk_threat

        # returns Tuple
        closest_friendly_position = world.util.get_closest_friendly_territory_from(friendly_unit.position, friendly_unit.body).position

        #calculate safety_turns/ returns int
        self.safety_turns = world.path.get_shortest_path_distance(friendly_unit.position, closest_friendly_position)

        '''
        print("Threat:" + str(self.threat_turns))
        print("Safety:" + str(self.safety_turns))
        #if we are safe, continue grabbing territory
        if self.safety_turns + 2 >= self.threat_turns:
            # returns list of tuples
            next_position = world.path.get_shortest_path(friendly_unit.position, closest_friendly_position, friendly_unit.body)[0]
            friendly_unit.move(next_position)
        # if you hit your territory again
        if closest_friendly_position in world.get_neighbours(friendly_unit.position).values():
            print("Closest_friendly_position:" + str(closest_friendly_position))
            closest_available_territory = world.util.get_closest_capturable_territory_from(friendly_unit.position, friendly_unit.body).position
            next_position = world.path.get_shortest_path(friendly_unit.position, closest_available_territory, friendly_unit.body)[0]
            friendly_unit.move(next_position)
        # if you hit a wall, head back to closest territory
        '''

        
