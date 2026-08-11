from __future__ import annotations

import pytest

from thefuck.rules.tsuru_login import get_new_command, match
from thefuck.types import Command

error_msg = (
    "Error: you're not authenticated or your session has expired.",
    (
        "You're not authenticated or your session has expired. "
        'Please use "login" command for authentication.'
    ),
)


@pytest.mark.parametrize(
    "command",
    [
        Command("tsuru app-shell", error_msg[0]),
        Command("tsuru app-log -f", error_msg[1]),
    ],
)
def test_match(command) -> None:
    assert match(command)


@pytest.mark.parametrize(
    "command",
    [
        Command("tsuru", ""),
        Command("tsuru app-restart", "Error: unauthorized"),
        Command("tsuru app-log -f", "Error: unparseable data"),
    ],
)
def test_not_match(command) -> None:
    assert not match(command)


@pytest.mark.parametrize(
    "command, new_command",
    [
        (Command("tsuru app-shell", error_msg[0]), "tsuru login && tsuru app-shell"),
        (Command("tsuru app-log -f", error_msg[1]), "tsuru login && tsuru app-log -f"),
    ],
)
def test_get_new_command(command, new_command) -> None:
    assert get_new_command(command) == new_command
