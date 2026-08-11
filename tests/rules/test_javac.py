from __future__ import annotations

import pytest

from thefuck.rules.javac import get_new_command, match
from thefuck.types import Command


@pytest.mark.parametrize(
    "command", [Command("javac foo", ""), Command("javac bar", "")]
)
def test_match(command) -> None:
    assert match(command)


@pytest.mark.parametrize(
    "command, new_command",
    [
        (Command("javac foo", ""), "javac foo.java"),
        (Command("javac bar", ""), "javac bar.java"),
    ],
)
def test_get_new_command(command, new_command) -> None:
    assert get_new_command(command) == new_command
