from __future__ import annotations

from thefuck.rules.cd_cs import get_new_command, match
from thefuck.types import Command


def test_match() -> None:
    assert match(Command("cs", "cs: command not found"))
    assert match(Command("cs /etc/", "cs: command not found"))


def test_get_new_command() -> None:
    assert get_new_command(Command("cs /etc/", "cs: command not found")) == "cd /etc/"
