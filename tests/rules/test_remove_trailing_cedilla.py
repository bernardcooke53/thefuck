from __future__ import annotations

import pytest

from thefuck.rules.remove_trailing_cedilla import CEDILLA, get_new_command, match
from thefuck.types import Command


@pytest.mark.parametrize(
    "command",
    [Command("wrong" + CEDILLA, ""), Command("wrong with args" + CEDILLA, "")],
)
def test_match(command) -> None:
    assert match(command)


@pytest.mark.parametrize(
    "command, new_command",
    [
        (Command("wrong" + CEDILLA, ""), "wrong"),
        (Command("wrong with args" + CEDILLA, ""), "wrong with args"),
    ],
)
def test_get_new_command(command, new_command) -> None:
    assert get_new_command(command) == new_command
