"""Definitions of harvestable resources and buildable blocks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ResourceDefinition:
    key: str
    display_name: str
    yield_item: str
    yield_amount: int


RESOURCE_DEFINITIONS: Dict[str, ResourceDefinition] = {
    "tree": ResourceDefinition("tree", "Tree", "wood", 2),
    "rock": ResourceDefinition("rock", "Rock", "stone", 2),
    "bush": ResourceDefinition("bush", "Berry Bush", "berries", 1),
}


RESOURCE_DISPLAY_NAMES = {
    "wood": "Wood",
    "stone": "Stone",
    "berries": "Berries",
}

BUILDABLE_BLOCKS = {
    "wood_block": {
        "display": "Wood Block",
        "cost": {"wood": 1},
    },
    "stone_block": {
        "display": "Stone Block",
        "cost": {"stone": 1},
    },
    "campfire": {
        "display": "Campfire",
        "cost": {"wood": 2, "stone": 1},
    },
}

FOOD_RESOURCES = {"berries"}
