from __future__ import annotations

from collections.abc import Callable
from typing import Any
import pytest
import pytest_mock

from thefuck.shells import Generic


@pytest.fixture
def shell():
    return Generic()


def test_from_shell(shell: Generic) -> None:
    assert shell.from_shell("pwd") == "pwd"


def test_to_shell(shell: Generic) -> None:
    assert shell.to_shell("pwd") == "pwd"


def test_and_(shell: Generic) -> None:
    assert shell.and_("ls", "cd") == "ls && cd"


def test_or_(shell: Generic) -> None:
    assert shell.or_("ls", "cd") == "ls || cd"


def test_get_aliases(shell: Generic) -> None:
    assert shell.get_aliases() == {}


def test_app_alias(shell: Generic) -> None:
    assert "alias fuck" in shell.app_alias("fuck")
    assert "alias FUCK" in shell.app_alias("FUCK")
    assert "thefuck" in shell.app_alias("fuck")
    assert "TF_ALIAS=fuck PYTHONIOENCODING" in shell.app_alias("fuck")
    assert "PYTHONIOENCODING=utf-8 thefuck" in shell.app_alias("fuck")


def test_get_history(
    history_lines: Callable[[list[str]], None], shell: Generic
) -> None:
    history_lines(["ls", "rm"])
    # We don't know what to do in generic shell with history lines,
    # so just ignore them:
    assert list(shell.get_history()) == []


def test_split_command(shell: Generic) -> None:
    assert shell.split_command("ls") == ["ls"]
    assert shell.split_command("echo café") == ["echo", "café"]


def test_how_to_configure(shell: Generic) -> None:
    assert shell.how_to_configure() is None


@pytest.mark.parametrize(
    "side_effect, expected_info, warn",
    [
        (["3.5.9"], "Generic Shell 3.5.9", False),
        ([OSError], "Generic Shell", True),
    ],
)
def test_info(
    side_effect: Any,
    expected_info: str,
    warn: bool,
    shell: Generic,
    mocker: pytest_mock.MockerFixture,
) -> None:
    warn_mock = mocker.patch("thefuck.shells.generic.warn")
    shell._get_version = mocker.Mock(side_effect=side_effect)
    assert shell.info() == expected_info
    assert warn_mock.called is warn
    assert shell._get_version.called
