from __future__ import annotations

import pytest

from thefuck.rules.git_merge import get_new_command, match
from thefuck.types import Command

output = (
    "merge: local - not something we can merge\n\nDid you mean this?\n\tremote/local"
)


def test_match() -> None:
    assert match(Command("git merge test", output))
    assert not match(Command("git merge master", ""))
    assert not match(Command("ls", output))


@pytest.mark.parametrize(
    "command, new_command",
    [
        (Command("git merge local", output), "git merge remote/local"),
        (
            Command('git merge -m "test" local', output),
            'git merge -m "test" remote/local',
        ),
        (
            Command('git merge -m "test local" local', output),
            'git merge -m "test local" remote/local',
        ),
    ],
)
def test_get_new_command(command, new_command) -> None:
    assert get_new_command(command) == new_command
