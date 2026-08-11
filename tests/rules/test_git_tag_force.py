from __future__ import annotations

import pytest

from thefuck.rules.git_tag_force import get_new_command, match
from thefuck.types import Command


@pytest.fixture
def output() -> str:
    return """fatal: tag 'alert' already exists"""


def test_match(output) -> None:
    assert match(Command("git tag alert", output))
    assert not match(Command("git tag alert", ""))


def test_get_new_command(output) -> None:
    assert get_new_command(Command("git tag alert", output)) == "git tag --force alert"
