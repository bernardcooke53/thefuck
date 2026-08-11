from __future__ import annotations

import pytest

from thefuck.rules.git_remote_delete import get_new_command, match
from thefuck.types import Command


def test_match() -> None:
    assert match(Command("git remote delete foo", ""))


@pytest.mark.parametrize(
    "command",
    [
        Command("git remote remove foo", ""),
        Command("git remote add foo", ""),
        Command("git commit", ""),
    ],
)
def test_not_match(command) -> None:
    assert not match(command)


@pytest.mark.parametrize(
    "command, new_command",
    [
        (Command("git remote delete foo", ""), "git remote remove foo"),
        (Command("git remote delete delete", ""), "git remote remove delete"),
    ],
)
def test_get_new_command(command, new_command) -> None:
    assert get_new_command(command) == new_command
