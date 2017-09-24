from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

import random
from random import shuffle
import copy
import math

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.split_explore = 0.6
        self.pertube_prob = 0.5
        self.reward = 0

        self.attack_gain = 10
        self.attack_loss = -10
        self.friendly_unit = -5

        self.permanent_tile = -30
        self.neural_tile = 15
        self.enemy_tile = 25
        self.friendly_tile = -5

        self.friendly_nest = 50
        self.enemy_nest = 40

        self.nest_workers = 3
        self.friends_too_close = -1
        self.print = True

        # get all walls
        self.all_wall_positions = []

        # directions
        self.up = (0, 1)
        self.down = (0, -1)
        self.left = (-1, 0)
        self.right = (1, 0)

        # energy model with gradient guidance
        self.friendly_nest_energy = 999
        self.enemy_nest_energy = -999
        self.decay_rate = 0.8
        self.energy_field = [[0 for j in range(19)] for i in range(19)]
        self.gradient_field = [[(0,0) for j in range(19)] for i in range(19)]

    def get_energy_difference(self, energy_field, x, y):
        diff = energy_field[x[0]][x[1]] - energy_field[y[0]][y[1]]
        return (-diff*(x[0]-y[0])), -diff(x[1]-y[1]))

    def get_norm(self, vector):
        return math.sqrt(vector[0]*vector[0] + vector[1]*vector[1])

    def get_dir_derivatives(self, world, dir, coord):
        target = (coord[0]+dir[0], coord[1]+dir[1])
        if world.is_wall(target):
            return (0, 0)
        else:
            return self.get_energy_difference(self.energy_field, coord, target)

    def update_tiles(self, world, friendly_units, enemy_units):
        self.friendly_nests = world.get_friendly_nest_positions()
        self.enemy_nests = world.get_enemy_nest_positions()

        # update the energy map on the entire grid
        for i in range(world.get_width()):
            for j in range(world.get_height()):
                if world.is_wall((i, j)):
                    self.all_wall_positions.append((i, j))
                    # self.energy_map[i][j] = 'X'
                    continue
                elif (i, j) in self.friendly_nests:
                    self.energy_field[i][j] = self.friendly_nest_energy
                elif (i, j) in self.enemy_nests:
                    self.energy_field[i][j] = self.enemy_nest_energy
                else:
                    self.energy_field[i][j] = sum([self.friendly_nest_energy*self.decay_rate**(self.get_taxicab_distance((i, j), (xd, yd))) for xd, yd in self.friendly_nests]) + \
                                             sum([self.friendly_nest_energy * self.decay_rate ** (self.get_taxicab_distance((i, j), (xd, yd))) for xd, yd in self.friendly_nests])
        # create gradient field
        for i in range(world.get_width()):
            for j in range(world.get_height()):
                if world.is_wall((i, j)):
                    self.all_wall_positions.append((i, j))
                    # self.gradient_field[i][j] = (0, 0)
                    continue
                else:
                    dir_derivative_up = self.get_dir_derivatives(world, self.up, (i, j))
                    dir_derivative_down = self.get_dir_derivatives(world, self.down, (i, j))
                    dir_derivative_left = self.get_dir_derivatives(world, self.left, (i, j))
                    dir_derivative_right = self.get_dir_derivatives(world, self.right, (i, j))

                    candidate_dir = (0, 0)
                    max_norm = 0
                    for dir in [dir_derivative_up, dir_derivative_down, dir_derivative_left, dir_derivative_right]:
                        if self.get_norm(dir) > max_norm:
                            candidate_dir = dir
                            max_norm = self.get_norm(dir)

                    self.gradient_field[i][j] = candidate_dir


    def create_nests(self, world, friendly_units, enemy_units):
        pass

    def attack_enemy(self, world, friendly_units, enemy_units):
        pass

    def attack_nests(self, world, friendly_units, enemy_units):
        pass

    def occupy_neutral_tiles(self, world, friendly_units, enemy_units):
        pass

    def guard_nests(self, world, friendly_units, enemy_units):
        pass

    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.
        
        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world

        for unit in friendly_units:
            closest_tile = world.get_closest_capturable_tile_from(unit.position, None).position
            # pertub_tile = (closest_tile[0]+pertub_x, closest_tile[1]+pertub_y)
            # path = world.get_shortest_path(unit.position,
            #                                world.get_closest_capturable_tile_from(unit.position, None).position,
            #                                None)
            path = world.get_shortest_path(unit.position,
                                           closest_tile,
                                           None)
            if self.print:
                print(self.update_tiles(world, friendly_units, enemy_units))
                self.print = False
            if path: world.move(unit, path[0])





