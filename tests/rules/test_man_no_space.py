from __future__ import annotations

from thefuck.rules.man_no_space import get_new_command, match
from thefuck.types import Command


def test_match() -> None:
    assert match(Command("mandiff", "mandiff: command not found"))
    assert not match(Command("", ""))


def test_get_new_command() -> None:
    assert get_new_command(Command("mandiff", "")) == "man diff"
