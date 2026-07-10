from __future__ import annotations

from decorator import decorator


@decorator
def sudo_support(fn, command):
    """Removes sudo before calling fn and adds it after."""
    if not command.script.startswith("sudo "):
        return fn(command)

    result = fn(command.update(script=command.script[5:]))

    if result and isinstance(result, str):
        return f"sudo {result}"
    if isinstance(result, list):
        return [f"sudo {x}" for x in result]
    return result
