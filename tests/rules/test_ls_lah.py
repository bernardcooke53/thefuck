from __future__ import annotations

from thefuck.rules.ls_lah import get_new_command, match
from thefuck.types import Command


def test_match() -> None:
    assert match(Command("ls", ""))
    assert match(Command("ls file.py", ""))
    assert match(Command("ls /opt", ""))
    assert not match(Command("ls -lah /opt", ""))
    assert not match(Command("pacman -S binutils", ""))
    assert not match(Command("lsof", ""))


def test_get_new_command() -> None:
    assert get_new_command(Command("ls file.py", "")) == "ls -lah file.py"
    assert get_new_command(Command("ls", "")) == "ls -lah"
