from __future__ import annotations

import pytest

from thefuck.rules.brew_unknown_command import _brew_commands, get_new_command, match
from thefuck.types import Command


@pytest.fixture
def brew_unknown_cmd() -> str:
    return """Error: Unknown command: inst"""


@pytest.fixture
def brew_unknown_cmd2() -> str:
    return """Error: Unknown command: instaa"""


def test_match(brew_unknown_cmd) -> None:
    assert match(Command("brew inst", brew_unknown_cmd))
    for command in _brew_commands():
        assert not match(Command("brew " + command, ""))


def test_get_new_command(brew_unknown_cmd, brew_unknown_cmd2) -> None:
    assert get_new_command(Command("brew inst", brew_unknown_cmd)) == [
        "brew list",
        "brew install",
        "brew uninstall",
    ]

    cmds = get_new_command(Command("brew instaa", brew_unknown_cmd2))
    assert "brew install" in cmds
    assert "brew uninstall" in cmds
