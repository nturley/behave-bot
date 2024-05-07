import sc2
from sc2.bot_ai import BotAI
import sc2.constants
import sc2.main
import sc2.maps
from sc2.player import Bot
from sc2.position import Point2
from sc2.unit import Unit

import numpy as np
import time

np.set_printoptions(threshold=np.inf, linewidth=np.inf, precision=0)

def in_bounds(pos, grid):
    return pos[0] >= 0 and pos[0] < grid.shape[0] and pos[1] >= 0 and pos[1] < grid.shape[1]

def get_neighbors(pos, grid):
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if not in_bounds((pos[0] + i, pos[1] + j), grid):
                continue
            yield {'pos':(pos[0] + i, pos[1] + j),'dist':1 if i == 0 or j == 0 else 1.4} 

def propagate_zeros(grid):
    last_set = np.argwhere(grid == 0)
    next_set = []
    while len(last_set) > 0:
        for pos in last_set:
            pos_dist = grid[pos[0], pos[1]]
            for n in get_neighbors(pos, grid):
                n_pos = n['pos']
                n_dist = n['dist']
                if grid[n_pos] > pos_dist + n_dist:
                    grid[n_pos] = pos_dist + n_dist
                    next_set.append(n_pos)
        last_set = next_set
        next_set = []

def walk_circle(cx, cy, radius):
    for r in range(int(radius * np.sqrt(0.5))):
        d = int(np.sqrt(radius*radius - r*r))
        yield (cx - d, cy + r)
        yield (cx + d, cy + r)
        yield (cx - d, cy - r)
        yield (cx + d, cy - r)
        yield (cx + r, cy - d)
        yield (cx + r, cy + d)
        yield (cx - r, cy - d)
        yield (cx - r, cy + d)

def draw_circle(grid, cx, cy, radius):
    for pos in walk_circle(cx, cy, radius):
        if in_bounds(pos, grid):
            grid[pos] = 1

def draw_splotch(grid, cx, cy, radius):
    for r in range(radius):
        for pos in walk_circle(cx, cy, r):
            if in_bounds(pos, grid):
                grid[pos] += (radius - r + 1) * 0.5

def max_pos(grid):
    return np.unravel_index(np.argmax(grid, axis=None), grid.shape)




class MyBot(BotAI):

    def init_wall_distance_grid(self, pathing_grid):
        wall_distance_grid = np.zeros(pathing_grid.shape, dtype=np.float32)
        wall_distance_grid[:] = 255
        wall_distance_grid *= pathing_grid
        propagate_zeros(wall_distance_grid)
        self.wall_distance_grid = wall_distance_grid
    
    def init_avoid_enemy_grid(self):
        avoid_enemy_grid = np.zeros(self.path_grid_shape, dtype=np.float32)
        avoid_enemy_grid[:] = 255
        for unit in self.all_enemy_units:
            e_pos = unit.position.rounded
            avoid_enemy_grid[e_pos] = 0
        propagate_zeros(avoid_enemy_grid)
        return avoid_enemy_grid
    
    def init_avoid_friendly_grid(self):
        avoid_friendly_grid = np.zeros(self.path_grid_shape, dtype=np.float32)
        avoid_friendly_grid[:] = 255
        for unit in self.all_own_units:
            m_pos = unit.position.rounded
            avoid_friendly_grid[m_pos] = 0
        propagate_zeros(avoid_friendly_grid)
        return avoid_friendly_grid
    
    def init_walk_circle_grid(self, pos, radius):
        walk_circle_grid = np.zeros(self.path_grid_shape, dtype=np.float32)
        draw_circle(walk_circle_grid, pos[0], pos[1], radius)
        return walk_circle_grid
    
    def avoid_position(self, pos):
        avoid_pos_grid = np.zeros(self.path_grid_shape, dtype=np.float32)
        avoid_pos_grid[:] = 255
        if pos is not None:
            avoid_pos_grid[pos] = 0
        propagate_zeros(avoid_pos_grid)
        return avoid_pos_grid


    async def on_start(self):
        self.client.game_step: int = 1
        pathing_grid = self.game_info.pathing_grid.data_numpy
        self.path_grid_shape = pathing_grid.shape
        self.init_wall_distance_grid(pathing_grid)
        self.last_pos = None
        self.last_move_cmd = 0
        self.pheromone_grid = np.zeros(self.path_grid_shape, dtype=np.float32)
        self.maurauders = None



    async def on_step(self, iteration: int):
        if self.maurauders is None:
            self.maurauders = [MyMaurauder(x, self) for x in self.all_own_units]
        self.pheromone_grid *= 0.9
        for my_m in self.maurauders:
            for m in self.all_own_units:
                if my_m.tag == m.tag:
                    my_m.step(iteration, m)
        time.sleep(0.02)

class MyMaurauder:
    WALK_REFRESH = 20

    def __init__(self, my: Unit, bot: MyBot) -> None:
        self.tag = my.tag
        self.bot = bot
        self.next_walk_frame = 0

    
    def step(self, iteration: int, me: Unit):
        my_pos = me.position.rounded
        self.drop_pheromone(my_pos)
        enemies = self.bot.all_enemy_units
        
        if len(enemies) > 0 and me.weapon_ready:
            closest_enemy = enemies.closest_to(me)
            me.attack(closest_enemy)
            self.next_walk_frame = iteration
        elif self.next_walk_frame < iteration:
            walk_circle_grid = self.bot.init_walk_circle_grid(my_pos, 5)
            avoid_enemy_grid = self.bot.init_avoid_enemy_grid()
            avoid_friendly_grid = self.bot.init_avoid_friendly_grid()
            score_grid = (avoid_enemy_grid * 2 + self.bot.wall_distance_grid - self.bot.pheromone_grid + avoid_friendly_grid) * walk_circle_grid * self.bot.game_info.placement_grid.data_numpy
            target = max_pos(score_grid)
            print(f'Target: {target}')
            me.move(Point2(target))
            self.next_walk_frame = iteration + MyMaurauder.WALK_REFRESH
    

    
    def drop_pheromone(self, my_pos):
        draw_splotch(self.bot.pheromone_grid, my_pos[0], my_pos[1], 3)


sc2.main.run_game(
    sc2.maps.get("kiteTraining"),
    [Bot(sc2.data.Race.Terran, MyBot())],
    realtime=False,
)