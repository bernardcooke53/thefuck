from __future__ import annotations

import pytest

from thefuck.rules.git_add_force import get_new_command, match
from thefuck.types import Command


@pytest.fixture
def output() -> str:
    return (
        "The following paths are ignored by one of your .gitignore files:\n"
        "dist/app.js\n"
        "dist/background.js\n"
        "dist/options.js\n"
        "Use -f if you really want to add them.\n"
    )


def test_match(output) -> None:
    assert match(Command("git add dist/*.js", output))
    assert not match(Command("git add dist/*.js", ""))


def test_get_new_command(output) -> None:
    assert (
        get_new_command(Command("git add dist/*.js", output))
        == "git add --force dist/*.js"
    )
