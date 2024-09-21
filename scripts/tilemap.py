import copy
import json

import pygame

from .tiles import Tile

AUTOTILE_MAP = {
    tuple(sorted ([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple (sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple (sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.map = {}
        self.offgrid_tiles = []

    def extract(self, id_pairs, keep=False):
        print("\n\nin extract: {}".format(id_pairs))
        # print("offgrid: {}\n\n".format(self.offgrid_tiles))
        # print("\n\nmap: {}\n\n".format(self.map))
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile.type, tile.variant) in id_pairs:
                matches.append(copy.deepcopy(tile))
                if not keep:
                    self.offgrid_tiles.remove(tile)

        print("\noffgrid done\n")
        
        for loc in copy.deepcopy(self.map):
            tile = self.map[loc]
            if (tile.type, tile.variant) in id_pairs:
                matches.append(copy.deepcopy(tile))
                matches[-1].pos = matches[-1].pos
                matches[-1].pos[0] *= self.tile_size
                matches[-1].pos[1] += self.tile_size
                if not keep:
                    del self.map[loc]

        print("\nmap done\n")
        
        return matches

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.map:
                tiles.append(self.map[check_loc])
        return tiles
    
    def save(self, path):
        f = open(path, 'w')
        json_tilemap = {key: value.get_dict() for key, value in self.map.items()}
        json_offgrid_tiles = [tile.get_dict() for tile in self.offgrid_tiles]
        json.dump({'tilemap': json_tilemap, 'tile_size': self.tile_size, 'offgrid': json_offgrid_tiles}, indent=4, fp=f)
        f.close()
    
    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.map:
            if self.map[tile_loc].type in PHYSICS_TILES:
                return self.map[tile_loc]

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        # convert dict and list with dicts to their Tile object counterparts before assigning
        obj_tilemap = {key: Tile(value['type'], value['variant'], (value['pos'][0], value['pos'][1])) for key, value in map_data['tilemap'].items()}
        obj_offgrid = [Tile(value['type'], value['variant'], (value['pos'][0], value['pos'][1])) for value in map_data['offgrid']]
        self.map = obj_tilemap
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = obj_offgrid
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile.type in PHYSICS_TILES:
                rects.append(pygame.Rect(tile.pos[0] * self.tile_size, tile.pos[1] * self.tile_size,
                                         self.tile_size, self.tile_size))
        return rects
    
    def autotile(self):
        for loc in self.map:
            tile = self.map[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile.pos[0] + shift[0]) + ';' + str(tile.pos[1] + shift[1])
                if check_loc in self.map:
                    if self.map[check_loc].type == tile.type:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile.type in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile.variant = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile.type][tile.variant],
                      (tile.pos[0] - offset[0], tile.pos[1] - offset[1]))
            

        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.map:
                    tile = self.map[loc]
                    surf.blit(self.game.assets[tile.type][tile.variant],
                      (tile.pos[0] * self.tile_size - offset[0],
                       tile.pos[1] * self.tile_size - offset[1]))
