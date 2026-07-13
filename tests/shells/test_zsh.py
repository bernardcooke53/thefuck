from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import pytest
import pytest_mock

from thefuck.shells.zsh import Zsh


@pytest.fixture
def shell():
    return Zsh()


@pytest.fixture(autouse=True)
def Popen(mocker: pytest_mock.MockerFixture):
    return mocker.patch("thefuck.shells.zsh.Popen")


@pytest.fixture(autouse=True)
def shell_aliases() -> None:
    os.environ["TF_SHELL_ALIASES"] = (
        "fuck='eval $(thefuck $(fc -ln -1 | tail -n 1))'\n"
        "l='ls -CF'\n"
        "la='ls -A'\n"
        "ll='ls -alF'"
    )


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "before, after",
    [
        ("fuck", "eval $(thefuck $(fc -ln -1 | tail -n 1))"),
        ("pwd", "pwd"),
        ("ll", "ls -alF"),
    ],
)
def test_from_shell(before: str, after: str, shell: Zsh) -> None:
    assert shell.from_shell(before) == after


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_to_shell(shell: Zsh) -> None:
    assert shell.to_shell("pwd") == "pwd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_and_(shell: Zsh) -> None:
    assert shell.and_("ls", "cd") == "ls && cd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_or_(shell: Zsh) -> None:
    assert shell.or_("ls", "cd") == "ls || cd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_aliases(shell: Zsh) -> None:
    assert shell.get_aliases() == {
        "fuck": "eval $(thefuck $(fc -ln -1 | tail -n 1))",
        "l": "ls -CF",
        "la": "ls -A",
        "ll": "ls -alF",
    }


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias(shell: Zsh) -> None:
    assert "fuck () {" in shell.app_alias("fuck")
    assert "FUCK () {" in shell.app_alias("FUCK")
    assert "thefuck" in shell.app_alias("fuck")
    assert "PYTHONIOENCODING" in shell.app_alias("fuck")


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias_variables_correctly_set(shell) -> None:
    alias = shell.app_alias("fuck")
    assert "fuck () {" in alias
    assert "TF_SHELL=zsh" in alias
    assert "TF_ALIAS=fuck" in alias
    assert "PYTHONIOENCODING=utf-8" in alias
    assert "TF_SHELL_ALIASES=$(alias)" in alias


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_history(history_lines: Callable[[list[str]], None], shell: Zsh) -> None:
    history_lines([": 1432613911:0;ls", ": 1432613916:0;rm"])
    assert list(shell.get_history()) == ["ls", "rm"]


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure(shell: Zsh, config_exists) -> None:
    config_exists.return_value = True
    assert shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure_when_config_not_found(shell: Zsh, config_exists) -> None:
    config_exists.return_value = False
    assert not shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_info(shell: Zsh, Popen) -> None:
    Popen.return_value.stdout.read.side_effect = [b"3.5.9"]
    assert shell.info() == "ZSH 3.5.9"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_version_error(shell: Zsh, Popen) -> None:
    Popen.return_value.stdout.read.side_effect = OSError
    with pytest.raises(OSError):
        shell._get_version()
    assert Popen.call_args[0][0] == ["zsh", "-c", "echo $ZSH_VERSION"]
