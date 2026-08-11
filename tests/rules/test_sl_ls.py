from __future__ import annotations

from thefuck.rules.sl_ls import get_new_command, match
from thefuck.types import Command


def test_match() -> None:
    assert match(Command("sl", ""))
    assert not match(Command("ls", ""))


def test_get_new_command() -> None:
    assert get_new_command(Command("sl", "")) == "ls"
