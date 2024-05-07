from py_trees.common import Status
from sc2.ids.unit_typeid import UnitTypeId
import py_trees
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pybehavbot.bot import MyBot as Bot

from sc2.unit import Unit
from sc2.position import Point2

class Train(py_trees.behaviour.Behaviour):
    def __init__(self, unitTypeName: str, key: str):
        super().__init__("Train")
        self.key = key
        self.unitTypeId = getattr(UnitTypeId, unitTypeName)
        self.blackboard = self.attach_blackboard_client(name="Train")
        self.blackboard.register_key(self.key, py_trees.common.Access.READ)
    
    def update(self) -> Status:
        self.blackboard.get(self.key).train(self.unitTypeId)
        return Status.SUCCESS


class Build(py_trees.behaviour.Behaviour):
    def __init__(self, unitTypeName: str, posKey: str, bot: 'Bot', builder: str):
        super().__init__("Build")
        self.posKey = posKey
        self.builder = builder
        self.unitTypeId = getattr(UnitTypeId, unitTypeName)
        self.blackboard = self.attach_blackboard_client(name="Build")
        self.blackboard.register_key(self.posKey, py_trees.common.Access.READ)
        self.blackboard.register_key(self.builder, py_trees.common.Access.READ)
        
        self.bot = bot
    
    def update(self) -> Status:
        pos = self.blackboard.get(self.posKey)
        builder: Unit = self.blackboard.get(self.builder)
        builder.build(self.unitTypeId, pos)
        return Status.SUCCESS


class GetSupplyLeft(py_trees.behaviour.Behaviour):
    def __init__(self, bot: 'Bot', key: str):
        super().__init__("Get Supply Left")
        self.key = key
        self.blackboard = self.attach_blackboard_client(name="Get Supply Left")
        self.blackboard.register_key(self.key, py_trees.common.Access.WRITE)
        self.bot = bot
    
    def update(self) -> Status:
        self.blackboard.set(self.key, self.bot.supply_left)
        return Status.SUCCESS


class CountPending(py_trees.behaviour.Behaviour):
    def __init__(self, bot: 'Bot', unitTypeName: str, key: str):
        super().__init__("Count Pending")
        self.unitTypeId = getattr(UnitTypeId, unitTypeName)
        self.key = key
        self.blackboard = self.attach_blackboard_client(name="Count Pending")
        self.blackboard.register_key(self.key, py_trees.common.Access.WRITE)
        self.bot = bot
    
    def update(self) -> Status:
        self.blackboard.set(self.key, self.bot.already_pending(self.unitTypeId))
        return Status.SUCCESS

class FindStructure(py_trees.behaviour.Behaviour):
    def __init__(self, bot: 'Bot', unitTypeName: str, key: str):
        super().__init__(name="Find Structure")
        self.unitTypeId = getattr(UnitTypeId, unitTypeName)
        self.key = key
        self.blackboard = self.attach_blackboard_client(name="Find Structure")
        self.blackboard.register_key(self.key, py_trees.common.Access.WRITE)
        self.bot = bot


    def update(self):
        found = self.bot.find_structure(self.unitTypeId)
        self.blackboard.set(self.key, found)
        if found:
          return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class FindUnit(py_trees.behaviour.Behaviour):
    def __init__(self, bot: 'Bot', unitTypeName: str, key: str):
        super().__init__(name="Find Unit")
        self.unitTypeId = getattr(UnitTypeId, unitTypeName)
        self.key = key
        self.blackboard = self.attach_blackboard_client(name="Find Unit")
        self.blackboard.register_key(self.key, py_trees.common.Access.WRITE)
        self.bot = bot


    def update(self):
        found = self.bot.all_own_units(self.unitTypeId).first
        self.blackboard.set(self.key, found)
        if found:
          return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class PositionOf(py_trees.behaviour.Behaviour):
    def __init__(self, bot: 'Bot', key: str, unitKey: str, scoot: int):
        super().__init__("Position Of")
        self.key = key
        self.blackboard = self.attach_blackboard_client(name="Position Of")
        self.blackboard.register_key(self.key, py_trees.common.Access.WRITE)
        self.blackboard.register_key(unitKey, py_trees.common.Access.READ)
        self.bot = bot
        self.scoot = scoot
        self.unitKey = unitKey
    
    def update(self) -> Status:
        unit: Unit = self.blackboard.get(self.unitKey)
        pos: Point2 = self.bot.game_info.map_center
        self.blackboard.set(self.key, unit.position.towards(pos, self.scoot))
        return Status.SUCCESS