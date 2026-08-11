from __future__ import annotations

import pytest

from thefuck.rules.php_s import get_new_command, match
from thefuck.types import Command


@pytest.mark.parametrize(
    "command",
    [Command("php -s localhost:8000", ""), Command("php -t pub -s 0.0.0.0:8080", "")],
)
def test_match(command) -> None:
    assert match(command)


@pytest.mark.parametrize(
    "command", [Command("php -S localhost:8000", ""), Command("vim php -s", "")]
)
def test_not_match(command) -> None:
    assert not match(command)


@pytest.mark.parametrize(
    "command, new_command",
    [
        (Command("php -s localhost:8000", ""), "php -S localhost:8000"),
        (Command("php -t pub -s 0.0.0.0:8080", ""), "php -t pub -S 0.0.0.0:8080"),
    ],
)
def test_get_new_command(command, new_command) -> None:
    assert get_new_command(command) == new_command
