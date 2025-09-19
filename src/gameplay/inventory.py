"""Inventory system handling stackable resources."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable

from ..engine.constants import MAX_STACK_SIZE


@dataclass
class Inventory:
    stacks: Dict[str, int] = field(default_factory=dict)

    def add(self, resource: str, amount: int = 1) -> None:
        current = self.stacks.get(resource, 0)
        self.stacks[resource] = min(MAX_STACK_SIZE, current + amount)

    def remove(self, resource: str, amount: int = 1) -> bool:
        current = self.stacks.get(resource, 0)
        if current < amount:
            return False
        new_amount = current - amount
        if new_amount <= 0:
            self.stacks.pop(resource, None)
        else:
            self.stacks[resource] = new_amount
        return True

    def amount(self, resource: str) -> int:
        return self.stacks.get(resource, 0)

    def items(self) -> Iterable[tuple[str, int]]:
        return self.stacks.items()
