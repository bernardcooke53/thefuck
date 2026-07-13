from __future__ import annotations

from thefuck.rules.cd_parent import get_new_command, match
from thefuck.types import Command


def test_match() -> None:
    assert match(Command("cd..", "cd..: command not found"))
    assert not match(Command("", ""))


def test_get_new_command() -> None:
    assert get_new_command(Command("cd..", "")) == "cd .."
