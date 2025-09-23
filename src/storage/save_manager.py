"""Helpers for persisting and loading Prismalia worlds."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

SAVE_DIR = Path("saves")


def _ensure_save_dir() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def list_worlds() -> List[Dict[str, Any]]:
    """Return metadata for all available world saves."""

    _ensure_save_dir()
    saves: List[Dict[str, Any]] = []
    for path in sorted(SAVE_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        metadata = dict(payload.get("metadata", {}))
        metadata.setdefault("slot_name", path.stem)
        metadata.setdefault("title", metadata["slot_name"])
        if "updated_at" not in metadata:
            metadata["updated_at"] = datetime.utcfromtimestamp(
                path.stat().st_mtime
            ).isoformat()
        if "created_at" not in metadata:
            metadata["created_at"] = metadata["updated_at"]
        saves.append(metadata)

    saves.sort(key=lambda meta: meta.get("updated_at", ""), reverse=True)
    return saves


def load_world(slot_name: str) -> "World":
    """Load a world for the provided save slot."""

    _ensure_save_dir()
    path = SAVE_DIR / f"{slot_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"No save found for slot '{slot_name}'")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    metadata = dict(payload.get("metadata", {}))
    metadata.setdefault("slot_name", slot_name)
    data = payload.get("world")
    if not isinstance(data, dict):
        raise ValueError(f"Invalid save data for slot '{slot_name}'")
    from ..gameplay.world import World

    return World.from_save(data, metadata)


def save_world(world: "World", slot_name: str) -> None:
    """Persist the provided world in the selected slot."""

    _ensure_save_dir()
    path = SAVE_DIR / f"{slot_name}.json"

    existing_metadata: Dict[str, Any] = {}
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            existing_metadata = dict(payload.get("metadata", {}))
        except (OSError, json.JSONDecodeError):
            existing_metadata = {}

    world_metadata: Dict[str, Any] = {
        "slot_name": slot_name,
        "title": getattr(world, "title", slot_name),
        "seed": int(getattr(world, "seed", 0)) if getattr(world, "seed", None) is not None else None,
        "size": [world.tilemap.width, world.tilemap.height],
        "player_position": [float(world.player.position.x), float(world.player.position.y)],
        "player_hunger": float(world.player.hunger),
        "animal_hunger": float(world.animal.hunger),
        "updated_at": datetime.utcnow().isoformat(),
    }
    world_metadata["created_at"] = existing_metadata.get(
        "created_at", world_metadata["updated_at"]
    )

    payload = {
        "metadata": world_metadata,
        "world": world.to_dict(),
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
