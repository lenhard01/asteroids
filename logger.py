import inspect
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

__all__ = ["log_event", "log_state"]

_FPS = 60
_MAX_SECONDS = 16
_SPRITE_SAMPLE_LIMIT = 10  # Maximum number of sprites to log per group


@dataclass
class _LogState:
    frame_count: int = 0
    state_log_initialized: bool = False
    event_log_initialized: bool = False


_log = _LogState()
_start_time = datetime.now(tz=UTC)


def _build_sprite_info(sprite: object) -> dict[str, object]:
    info: dict[str, object] = {"type": sprite.__class__.__name__}
    if hasattr(sprite, "position"):
        info["pos"] = [
            round(sprite.position.x, 2),
            round(sprite.position.y, 2),
        ]
    if hasattr(sprite, "velocity"):
        info["vel"] = [
            round(sprite.velocity.x, 2),
            round(sprite.velocity.y, 2),
        ]
    if hasattr(sprite, "radius"):
        info["rad"] = sprite.radius
    if hasattr(sprite, "rotation"):
        info["rot"] = round(sprite.rotation, 2)
    return info


def _extract_game_state(
    local_vars: dict[str, object],
) -> tuple[list[int], dict[str, object]]:
    screen_size: list[int] = []
    game_state: dict[str, object] = {}

    for key, value in local_vars.items():
        if "pygame" in str(type(value)) and hasattr(value, "get_size"):
            screen_size = value.get_size()

        if hasattr(value, "__class__") and "Group" in value.__class__.__name__:
            sprites_data = [
                _build_sprite_info(sprite)
                for i, sprite in enumerate(value)
                if i < _SPRITE_SAMPLE_LIMIT
            ]
            game_state[key] = {"count": len(value), "sprites": sprites_data}

        elif not game_state and hasattr(value, "position"):
            game_state[key] = _build_sprite_info(value)

    return screen_size, game_state


def log_state() -> None:
    # Stop logging after `_MAX_SECONDS` seconds
    if _log.frame_count > _FPS * _MAX_SECONDS:
        return

    # Take a snapshot approx. once per second
    _log.frame_count += 1
    if _log.frame_count % _FPS != 0:
        return

    now = datetime.now(tz=UTC)
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        return

    local_vars: dict[str, object] = frame.f_back.f_locals.copy()
    screen_size, game_state = _extract_game_state(local_vars)

    entry: dict[str, object] = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _log.frame_count,
        "screen_size": screen_size,
        **game_state,
    }

    # New log file on each run
    mode = "w" if not _log.state_log_initialized else "a"
    with Path("game_state.jsonl").open(mode) as f:
        f.write(json.dumps(entry) + "\n")
    _log.state_log_initialized = True


def log_event(event_type: str, **details: object) -> None:
    now = datetime.now(tz=UTC)

    event: dict[str, object] = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _log.frame_count,
        "type": event_type,
        **details,
    }

    mode = "w" if not _log.event_log_initialized else "a"
    with Path("game_events.jsonl").open(mode) as f:
        f.write(json.dumps(event) + "\n")
    _log.event_log_initialized = True
