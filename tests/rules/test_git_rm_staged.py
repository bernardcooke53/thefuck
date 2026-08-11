from __future__ import annotations

import pytest

from thefuck.rules.git_rm_staged import get_new_command, match
from thefuck.types import Command


@pytest.fixture
def output(target) -> str:
    return (
        f"error: the following file has changes staged in the index:\n    {target}\n(use "
        "--cached to keep the file, or -f to force removal)"
    )


@pytest.mark.parametrize(
    "script, target", [("git rm foo", "foo"), ("git rm foo bar", "bar")]
)
def test_match(output, script, target) -> None:
    assert match(Command(script, output))


@pytest.mark.parametrize("script", ["git rm foo", "git rm foo bar", "git rm"])
def test_not_match(script) -> None:
    assert not match(Command(script, ""))


@pytest.mark.parametrize(
    "script, target, new_command",
    [
        ("git rm foo", "foo", ["git rm --cached foo", "git rm -f foo"]),
        ("git rm foo bar", "bar", ["git rm --cached foo bar", "git rm -f foo bar"]),
    ],
)
def test_get_new_command(output, script, target, new_command) -> None:
    assert get_new_command(Command(script, output)) == new_command
