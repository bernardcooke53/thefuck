from __future__ import annotations

import pytest

from thefuck.rules.git_diff_no_index import get_new_command, match
from thefuck.types import Command


@pytest.mark.parametrize("command", [Command("git diff foo bar", "")])
def test_match(command) -> None:
    assert match(command)


@pytest.mark.parametrize(
    "command",
    [
        Command("git diff --no-index foo bar", ""),
        Command("git diff foo", ""),
        Command("git diff foo bar baz", ""),
    ],
)
def test_not_match(command) -> None:
    assert not match(command)


@pytest.mark.parametrize(
    "command, new_command",
    [(Command("git diff foo bar", ""), "git diff --no-index foo bar")],
)
def test_get_new_command(command, new_command) -> None:
    assert get_new_command(command) == new_command
