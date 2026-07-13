from __future__ import annotations

from collections.abc import Callable
from typing import Any

from thefuck import types
from thefuck.const import DEFAULT_PRIORITY


class Rule(types.Rule):
    def __init__(
        self,
        name: str = "",
        match: Callable[..., bool] = lambda *_: True,
        get_new_command: Callable[..., str] = lambda *_: "",
        enabled_by_default: bool = True,
        side_effect: Callable[[types.Command, str], Any] | None = None,
        priority: int = DEFAULT_PRIORITY,
        requires_output: bool = True,
    ):
        super().__init__(
            name,
            match,
            get_new_command,
            enabled_by_default,
            side_effect,
            priority,
            requires_output,
        )


class CorrectedCommand(types.CorrectedCommand):
    def __init__(
        self,
        script: str = "",
        side_effect: Callable[[types.Command, str], Any] | None = None,
        priority: int = DEFAULT_PRIORITY,
    ) -> None:
        super().__init__(script, side_effect, priority)
