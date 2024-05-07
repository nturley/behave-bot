from py_trees.common import Status

import sc2
from sc2.bot_ai import BotAI
import sc2.constants
import sc2.main
import sc2.maps
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
import py_trees

from pybehavbot.behaviors.tree import build_tree

import json

class MyBot(BotAI):
    def __init__(self):
        super().__init__()
        root = build_tree(self)
        self.tree = py_trees.trees.BehaviourTree(
          root=root
        )
        

    async def on_start(self):
        print('Hello, SC2!')
        base_data = {
            "start": self.start_location,
            "ramp": {
                "corner_depots": [x for x in self.main_base_ramp.corner_depots],
                "barracks": self.main_base_ramp.barracks_in_middle,
            },
            "region": [x for x in self.game_info.placement_grid.flood_fill(self.start_location.rounded, lambda p: p == 1)],
            "mineral": [x.position for x in self.mineral_field],
            "geysers": [x.position for x in self.vespene_geyser]
        }

        with open('base_data.json', 'w') as f:
            json.dump(base_data, f)

        
    
    def find_structure(self, unitTypeId: UnitTypeId) -> Unit:
        return self.structures(unitTypeId).first

    async def on_step(self, iteration: int):
        
        self.tree.tick()


def run():
    sc2.main.run_game(
        sc2.maps.get("SiteDelta512V2AIE"),
        [Bot(sc2.data.Race.Terran, MyBot()), Computer(sc2.data.Race.Zerg, sc2.data.Difficulty.Hard)],
        realtime=False,
    )



