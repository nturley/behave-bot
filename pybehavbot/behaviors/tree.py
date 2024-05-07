import json

import py_trees
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pybehavbot.bot import MyBot as Bot
from pybehavbot.behaviors.actions import Train, FindStructure, Build, GetSupplyLeft, CountPending, PositionOf, FindUnit
from pybehavbot.behaviors.conditions import CanAfford, IsIdle, CompareValue
from pathlib import Path

tree_path = Path(__file__).resolve().parent.parent / 'tree.json'


def build_tree(bot: 'Bot'):
    with open(tree_path) as f:
        j = json.load(f)
    root = j["nodes"][j["root"]]
    return build_node(j["nodes"], root, bot)


def build_node(jnodes: list, jnode: dict, bot: 'Bot'):
    name = jnode["name"]
    children = jnode.get("children", [])
    props = jnode["properties"]
    if name == "Sequence":
        node = py_trees.composites.Sequence(name, False)
        node.add_children([
            build_node(jnodes, jnodes[x], bot) for x in children
        ])
        return node
    elif name == "Train":
        return Train(props["unitType"], props["trainer"])
    elif name == "Can Afford?":
        return CanAfford(bot, props["UnitType"])
    elif name == "Idle?":
        return IsIdle(props["label"])
    elif name == "Find Structure":
        return FindStructure(bot, props["UnitType"], props["label"])
    elif name == "Find Unit":
        return FindUnit(bot, props["unitType"], props["key"])
    elif name == 'Priority':
        node = py_trees.composites.Selector(name, False)
        node.add_children([
            build_node(jnodes, jnodes[x], bot) for x in children
        ])
        return node
    elif name == "Check Supply Left":
        return GetSupplyLeft(bot, props["label"])
    elif name == "Compare":
        return CompareValue(bot, props["label"], int(props["value"]), props["op"])
    elif name == "Count Pending":
        return CountPending(bot, props["UnitType"], props["label"])
    elif name == "build":
        return Build(props["structType"], props["pos"], bot, props["builder"])
    elif name == "getPosFromUnit":
        return PositionOf(bot, props["label"], props["unit"], int(props["steps"]))
    
    raise Exception(f"Unknown node type: {name}")