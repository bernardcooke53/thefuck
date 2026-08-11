from __future__ import annotations

from thefuck.rules.ls_all import get_new_command, match
from thefuck.types import Command


def test_match() -> None:
    assert match(Command("ls", ""))
    assert not match(Command("ls", "file.py\n"))


def test_get_new_command() -> None:
    assert get_new_command(Command("ls empty_dir", "")) == "ls -A empty_dir"
    assert get_new_command(Command("ls", "")) == "ls -A"
