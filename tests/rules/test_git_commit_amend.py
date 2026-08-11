from __future__ import annotations

import pytest

from thefuck.rules.git_commit_amend import get_new_command, match
from thefuck.types import Command


@pytest.mark.parametrize(
    "script, output", [('git commit -m "test"', "test output"), ("git commit", "")]
)
def test_match(output, script) -> None:
    assert match(Command(script, output))


@pytest.mark.parametrize(
    "script", ["git branch foo", "git checkout feature/test_commit", "git push"]
)
def test_not_match(script) -> None:
    assert not match(Command(script, ""))


@pytest.mark.parametrize("script", [('git commit -m "test commit"'), ("git commit")])
def test_get_new_command(script) -> None:
    assert get_new_command(Command(script, "")) == "git commit --amend"
