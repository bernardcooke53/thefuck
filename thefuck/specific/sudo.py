from __future__ import annotations
from typing import Callable, TypeVar

from decorator import decorator

_R = TypeVar("_R")


@decorator
def sudo_support(fn: Callable[[str], _R], command: str) -> _R:
    """Removes sudo before calling fn and adds it after."""
    if not command.script.startswith("sudo "):
        return fn(command)

    result = fn(command.update(script=command.script[5:]))

    if result and isinstance(result, str):
        return f"sudo {result}"
    if isinstance(result, list):
        return [f"sudo {x}" for x in result]
    return result
