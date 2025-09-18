"""Inventory and resource management structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Inventory:
    """Simple stack based inventory."""

    slots: Dict[str, int] = field(default_factory=dict)
    capacity: int = 32

    def add(self, resource: str, amount: int = 1) -> None:
        if amount <= 0:
            return
        current = self.slots.get(resource, 0)
        self.slots[resource] = current + amount

    def remove(self, resource: str, amount: int = 1) -> bool:
        current = self.slots.get(resource, 0)
        if current < amount:
            return False
        new_amount = current - amount
        if new_amount <= 0:
            self.slots.pop(resource, None)
        else:
            self.slots[resource] = new_amount
        return True

    def has(self, resource: str, amount: int = 1) -> bool:
        return self.slots.get(resource, 0) >= amount

    def total_items(self) -> int:
        return sum(self.slots.values())

    def to_lines(self) -> list[str]:
        return [f"{key}: {amount}" for key, amount in sorted(self.slots.items())]
