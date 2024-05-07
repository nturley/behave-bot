import py_trees
from py_trees.common import Status

from sc2.ids.unit_typeid import UnitTypeId
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pybehavbot.bot import MyBot as Bot

class CanAfford(py_trees.behaviour.Behaviour):
    def __init__(self, bot: 'Bot', unitTypeName: str):
        super().__init__("Can Afford")
        self.unitTypeId = getattr(UnitTypeId, unitTypeName)
        self.bot = bot
    
    def update(self) -> Status:
        if self.bot.can_afford(self.unitTypeId):
            return Status.SUCCESS
        return Status.FAILURE


class CompareValue(py_trees.behaviour.Behaviour):
    def __init__(self, bot: 'Bot', key: str, value: int, comparison: str):
        super().__init__("Compare Value")
        self.key = key
        self.value = value
        self.comparison = comparison
        self.blackboard = self.attach_blackboard_client(name="Compare Value")
        self.blackboard.register_key(self.key, py_trees.common.Access.READ)
        self.bot = bot
    
    def update(self) -> Status:
        value = self.blackboard.get(self.key)
        if self.comparison == ">":
            if value > self.value:
                return Status.SUCCESS
        elif self.comparison == "<":
            if value < self.value:
                return Status.SUCCESS
        return Status.FAILURE


class IsIdle(py_trees.behaviour.Behaviour):
    def __init__(self, key: str):
        super().__init__(name="Is Idle")
        self.key = key
        self.blackboard = self.attach_blackboard_client(name="Is Idle")
        self.blackboard.register_key(self.key, py_trees.common.Access.READ)

    def update(self):
        unit = self.blackboard.get(self.key)
        if unit.is_idle:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE