from __future__ import annotations

import pytest

from thefuck.rules.ag_literal import get_new_command, match
from thefuck.types import Command


@pytest.fixture
def output() -> str:
    return (
        "ERR: Bad regex! pcre_compile() failed at position 1: missing )\n"
        "If you meant to search for a literal string, run ag with -Q\n"
    )


@pytest.mark.parametrize("script", ["ag \\("])
def test_match(script: str, output: str) -> None:
    assert match(Command(script, output))


@pytest.mark.parametrize("script", ["ag foo"])
def test_not_match(script: str) -> None:
    assert not match(Command(script, ""))


@pytest.mark.parametrize("script, new_cmd", [("ag \\(", "ag -Q \\(")])
def test_get_new_command(script: str, new_cmd: str, output: str) -> None:
    assert get_new_command(Command(script, output)) == new_cmd
