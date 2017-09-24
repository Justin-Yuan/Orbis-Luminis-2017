from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

import random
from random import shuffle
import copy

class PlayerAI:

    def __init__(self):
        """
        Any instantiation code goes here
        """
        self.split_explore = 0.7
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

    def get_adjacent_pts(self, world, cur_tile):
        return list(world.get_neighbours(cur_tile.position).values())


    def num_potential_nests(self, world, cur_tile):
        num_nests = 0
        neighbours = self.get_adjacent_pts(world, cur_tile)
        for n in neighbours:
            # print(n, type(world.get_tile_at(n)))
            if world.get_tile_at(n) != None and world.get_tile_at(n).is_neutral():
                n_neighbours = self.get_adjacent_pts(world, world.get_tile_at(n))
                count = 0
                for n2 in n_neighbours:
                    temp_tile = world.get_tile_at(n2)
                    # print(n2, type(temp_tile))
                    if temp_tile == None or temp_tile.is_friendly() and temp_tile.position != cur_tile.position:
                        count += 1
                if count == len(n_neighbours) - 1:
                    num_nests += 1
        return num_nests

    def greedy_search(self, world, friendly_units, enemy_units, unit, cur_tile, next_tile):
        """
        
        :param world: 
        :param friendly_units: 
        :param enemy_units: 
        :return: 
        """
        # num_friendly_units = len(friendly_units)
        # num_enemy_units = len(enemy_units)
        # num_friendly_tiles = len(world.get_friendly_tiles())
        # num_enemy_tiles = len(world.get_enemy_tiles())
        # num_friendly_nests = len(world.get_friendly_nest_positions())
        # num_enemy_nests = len(world.get_enemy_nest_positions())
        #
        # new_reward = 10*num_friendly_units - 5*num_enemy_units + \
        #     8*num_friendly_tiles - 4*num_enemy_tiles + \
        #     4*num_friendly_nests - 2*num_enemy_nests

        reward = 0
        closest_enemy = world.get_closest_enemy_from(cur_tile.position, None)

        if next_tile.is_permanently_owned():
            reward += self.permanent_tile
        elif next_tile.is_enemy():
            reward += self.enemy_tile
        elif next_tile.is_neutral():
            reward += self.neural_tile
        elif next_tile.is_friendly():
            reward += self.friendly_tile

        if (next_tile.position == closest_enemy.position or closest_enemy.position in self.get_adjacent_pts(world, next_tile)) and unit.health >= closest_enemy.health:
            reward += self.attack_gain
        elif (next_tile.position == closest_enemy.position or closest_enemy.position in self.get_adjacent_pts(world, next_tile)) and unit.health < closest_enemy.health:
            reward += self.attack_loss

        closest_friend = world.get_closest_friendly_from(next_tile.position, None)
        dis = world.get_shortest_path_distance(next_tile.position, closest_friend.position)
        reward += self.friends_too_close *(world.get_height() - dis)

        # if self.is_nest(world, next_tile):
        reward += self.num_potential_nests(world, next_tile)*self.friendly_nest

        enemy_nests = world.get_enemy_nest_positions()
        enemy_nests_pos = []
        for ene_nest in enemy_nests:
            enemy_nests_pos.extend(self.get_adjacent_pts(world, world.get_tile_at(ene_nest)))
        if next_tile.position in enemy_nests_pos:
            reward += self.enemy_nest

        return reward



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

        length = len(friendly_units)
        split_pt = 0 #length
        # split_pt = int(length*self.split_explore)
        # if length > 20:
        #     friendly_units.sort(key=lambda v: v.health)
        #     split_pt = int(len(friendly_units)*self.split_explore)
        #
        #     for unit in friendly_units[split_pt:]:
        #
        #         neural_tile = world.get_closest_neutral_tile_from(unit.position, None).position
        #         neural_neigh_tiles = world.get_tiles_around(neural_tile)
        #         neigh_tile_distance = {pt: get_shortest_path_distance(unit.position, pt) for pt in neural_neigh_tiles}
        #         closest_neural_neight_tile = min(neigh_tile_distance, key=neigh_tile_distance.get)
        #         distance = neigh_tile_distance[closest_neural_neight_tile]
        #
        #         path = world.get_shortest_path(unit.position,
        #                                        closest_neural_neight_tile,
        #                                        None)
        #         if distance >= 2:
        #             if path: world.move(unit, path[0])
        #         else:
        #             if closest_neural_neight_tile[0] == path[0][0]:
        #                 side_tile = (path[0][0]+1, path[0][1])
        #             elif closest_neural_neight_tile[1] == path[0][1]:
        #                 side_tile = (path[0][0], path[0][1]+1)
        #             else:
        #                 side_tile = path[0]
        #             world.move(unit, side_tile)

        # pertub_x = -1 if random.random() > self.pertube_prob else 1
        # pertub_y = 1 if random.random() > self.pertube_prob else -1

        # if length > 70:
        #     for unit in friendly_units:
        #         closest_tile = world.get_closest_capturable_tile_from(unit.position, None).position
        #         # pertub_tile = (closest_tile[0]+pertub_x, closest_tile[1]+pertub_y)
        #         # path = world.get_shortest_path(unit.position,
        #         #                                world.get_closest_capturable_tile_from(unit.position, None).position,
        #         #                                None)
        #         path = world.get_shortest_path(unit.position,
        #                                        closest_tile,
        #                                        None)
        #         if path: world.move(unit, path[0])
        # elif length > 50:
        #     for unit in friendly_units[split_pt:]:
        #         closest_tile = world.get_closest_capturable_tile_from(unit.position, None).position
        #         # pertub_tile = (closest_tile[0]+pertub_x, closest_tile[1]+pertub_y)
        #         # path = world.get_shortest_path(unit.position,
        #         #                                world.get_closest_capturable_tile_from(unit.position, None).position,
        #         #                                None)
        #         path = world.get_shortest_path(unit.position,
        #                                        closest_tile,
        #                                        None)
        #         if path: world.move(unit, path[0])
        #
        #     # for unit in friendly_units[split_pt:]:
        #     #     reward = -999
        #     #     new_pt = None
        #     #     candidate_pts = [(unit.position[0]+1, unit.position[1]), (unit.position[0], unit.position[1]+1), \
        #     #                      (unit.position[0]-1, unit.position[1]), (unit.position[0], unit.position[1]-1)]
        #     #     for pt in candidate_pts:
        #     #         world_copy = copy.deepcopy(world)
        #     #         world_copy.move(unit, pt)
        #     #         new_reward = self.greedy_search(world_copy, friendly_units, enemy_units)
        #     #         if new_reward > reward:
        #     #             reward = new_reward
        #     #             new_pt = pt
        #     #         del world_copy
        #     #     print(reward)
        #     #     world.move(unit, new_pt)
        #
        #     for unit in friendly_units[:split_pt]:
        #         neigh_tiles = world.get_neighbours(unit.position)
        #         cur_reward = -999
        #         next_position = unit.position
        #         l = [world.get_tile_at(item[1]) for item in neigh_tiles.items()]
        #         shuffle(l)
        #         for tile in l:
        #             if tile != None:
        #                 new_reward = self.greedy_search(world, friendly_units, enemy_units, unit, world.get_tile_at(unit.position), tile)
        #                 if new_reward > cur_reward:
        #                     cur_reward = new_reward
        #                     next_position = tile.position
        #         world.move(unit, next_position)
        # else:
        #     for unit in friendly_units:
        #         neigh_tiles = world.get_neighbours(unit.position)
        #         cur_reward = -999
        #         next_position = unit.position
        #         l = [world.get_tile_at(item[1]) for item in neigh_tiles.items()]
        #         shuffle(l)
        #         for tile in l:
        #             if tile != None:
        #                 new_reward = self.greedy_search(world, friendly_units, enemy_units, unit,
        #                                                 world.get_tile_at(unit.position), tile)
        #                 if new_reward > cur_reward:
        #                     cur_reward = new_reward
        #                     next_position = tile.position
        #         world.move(unit, next_position)

        for unit in friendly_units[split_pt:]:
            closest_tile = world.get_closest_capturable_tile_from(unit.position, None).position
            # pertub_tile = (closest_tile[0]+pertub_x, closest_tile[1]+pertub_y)
            # path = world.get_shortest_path(unit.position,
            #                                world.get_closest_capturable_tile_from(unit.position, None).position,
            #                                None)
            path = world.get_shortest_path(unit.position,
                                           closest_tile,
                                           None)
            if path: world.move(unit, path[0])

        # for unit in friendly_units[split_pt:]:
        #     reward = -999
        #     new_pt = None
        #     candidate_pts = [(unit.position[0]+1, unit.position[1]), (unit.position[0], unit.position[1]+1), \
        #                      (unit.position[0]-1, unit.position[1]), (unit.position[0], unit.position[1]-1)]
        #     for pt in candidate_pts:
        #         world_copy = copy.deepcopy(world)
        #         world_copy.move(unit, pt)
        #         new_reward = self.greedy_search(world_copy, friendly_units, enemy_units)
        #         if new_reward > reward:
        #             reward = new_reward
        #             new_pt = pt
        #         del world_copy
        #     print(reward)
        #     world.move(unit, new_pt)

        for unit in friendly_units[:split_pt]:
            neigh_tiles = world.get_neighbours(unit.position)
            cur_reward = -999
            next_position = unit.position
            l = [world.get_tile_at(item[1]) for item in neigh_tiles.items()]
            shuffle(l)
            for tile in l:
                if tile != None:
                    new_reward = self.greedy_search(world, friendly_units, enemy_units, unit, world.get_tile_at(unit.position), tile)
                    if new_reward > cur_reward:
                        cur_reward = new_reward
                        next_position = tile.position
            world.move(unit, next_position)
        for unit in friendly_units[split_pt:]:
            closest_tile = world.get_closest_capturable_tile_from(unit.position, None).position
            # pertub_tile = (closest_tile[0]+pertub_x, closest_tile[1]+pertub_y)
            # path = world.get_shortest_path(unit.position,
            #                                world.get_closest_capturable_tile_from(unit.position, None).position,
            #                                None)
            attack_pos = world.get_closest_enemy_nest_from(unit.position, None)
            path = world.get_shortest_path(unit.position,
                                           attack_pos,
                                           world.get_closest_enemy_tile_from(unit.position, None).position)
            if path: world.move(unit, path[0])





