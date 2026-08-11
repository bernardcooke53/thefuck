from __future__ import annotations
import pytest_mock

import pytest

from thefuck.rules.apt_get import get_new_command, match
from thefuck.types import Command


@pytest.mark.parametrize(
    "command, packages",
    [
        (
            Command("vim", "vim: command not found"),
            [("vim", "main"), ("vim-tiny", "main")],
        ),
        (
            Command("sudo vim", "vim: command not found"),
            [("vim", "main"), ("vim-tiny", "main")],
        ),
        (
            Command(
                "vim",
                "The program 'vim' is currently not installed. You can install it by typing: sudo apt install vim",
            ),
            [("vim", "main"), ("vim-tiny", "main")],
        ),
    ],
)
def test_match(
    mocker: pytest_mock.MockFixture, command: str, packages: list[str]
) -> None:
    mocker.patch("shutil.which", return_value=None)
    mocker.patch(
        "thefuck.rules.apt_get._get_packages", create=True, return_value=packages
    )

    assert match(command)


@pytest.mark.parametrize(
    "command, packages, which",
    [
        (Command("a_bad_cmd", "a_bad_cmd: command not found"), [], None),
        (Command("vim", ""), [], None),
        (Command("", ""), [], None),
        (Command("vim", "vim: command not found"), ["vim"], "/usr/bin/vim"),
        (Command("sudo vim", "vim: command not found"), ["vim"], "/usr/bin/vim"),
    ],
)
def test_not_match(
    mocker: pytest_mock.MockFixture,
    command: str,
    packages: list[str],
    which: str | None,
) -> None:
    mocker.patch("shutil.which", return_value=which)
    mocker.patch(
        "thefuck.rules.apt_get._get_packages", create=True, return_value=packages
    )

    assert not match(command)


@pytest.mark.parametrize(
    "command, new_command, packages",
    [
        (
            Command("vim", ""),
            "sudo apt-get install vim && vim",
            [("vim", "main"), ("vim-tiny", "main")],
        ),
        (
            Command("convert", ""),
            "sudo apt-get install imagemagick && convert",
            [
                ("imagemagick", "main"),
                ("graphicsmagick-imagemagick-compat", "universe"),
            ],
        ),
        (
            Command("sudo vim", ""),
            "sudo apt-get install vim && sudo vim",
            [("vim", "main"), ("vim-tiny", "main")],
        ),
        (
            Command("sudo convert", ""),
            "sudo apt-get install imagemagick && sudo convert",
            [
                ("imagemagick", "main"),
                ("graphicsmagick-imagemagick-compat", "universe"),
            ],
        ),
    ],
)
def test_get_new_command(
    mocker: pytest_mock.MockFixture, command: str, new_command: str, packages: list[str]
) -> None:
    mocker.patch(
        "thefuck.rules.apt_get._get_packages", create=True, return_value=packages
    )

    assert get_new_command(command) == new_command
