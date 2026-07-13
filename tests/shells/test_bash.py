from __future__ import annotations

import os
from collections.abc import Callable

import pytest
import pytest_mock

from thefuck.shells import Bash


@pytest.fixture
def shell():
    return Bash()


@pytest.fixture(autouse=True)
def Popen(mocker):
    mock = mocker.patch("thefuck.shells.bash.Popen")
    return mock


@pytest.fixture(autouse=True)
def shell_aliases():
    os.environ["TF_SHELL_ALIASES"] = (
        "alias fuck='eval $(thefuck $(fc -ln -1))'\n"
        "alias l='ls -CF'\n"
        "alias la='ls -A'\n"
        "alias ll='ls -alF'"
    )


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "before, after",
    [
        ("pwd", "pwd"),
        ("fuck", "eval $(thefuck $(fc -ln -1))"),
        ("awk", "awk"),
        ("ll", "ls -alF"),
    ],
)
def test_from_shell(before: str, after: str, shell: Bash):
    assert shell.from_shell(before) == after


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_to_shell(shell: Bash):
    assert shell.to_shell("pwd") == "pwd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_and_(shell: Bash):
    assert shell.and_("ls", "cd") == "ls && cd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_or_(shell: Bash):
    assert shell.or_("ls", "cd") == "ls || cd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_aliases(shell: Bash):
    assert shell.get_aliases() == {
        "fuck": "eval $(thefuck $(fc -ln -1))",
        "l": "ls -CF",
        "la": "ls -A",
        "ll": "ls -alF",
    }


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias(shell: Bash):
    assert "fuck () {" in shell.app_alias("fuck")
    assert "FUCK () {" in shell.app_alias("FUCK")
    assert "thefuck" in shell.app_alias("fuck")
    assert "PYTHONIOENCODING" in shell.app_alias("fuck")


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias_variables_correctly_set(shell: Bash):
    alias = shell.app_alias("fuck")
    assert "fuck () {" in alias
    assert "TF_SHELL=bash" in alias
    assert "TF_ALIAS=fuck" in alias
    assert "PYTHONIOENCODING=utf-8" in alias
    assert "TF_SHELL_ALIASES=$(alias)" in alias


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_history(history_lines: Callable[[list[str]], None], shell: Bash):
    history_lines(["ls", "rm"])
    assert list(shell.get_history()) == ["ls", "rm"]


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_split_command(shell: Bash):
    command = "git log -p"
    command_parts = ["git", "log", "-p"]
    assert shell.split_command(command) == command_parts


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure(shell: Bash, config_exists):
    config_exists.return_value = True
    assert shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure_when_config_not_found(shell: Bash, config_exists):
    config_exists.return_value = False
    assert not shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_info(shell: Bash, Popen: pytest_mock.MockType):
    Popen.return_value.stdout.read.side_effect = [b"3.5.9"]
    assert shell.info() == "Bash 3.5.9"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_version_error(shell: Bash, Popen: pytest_mock.MockType):
    Popen.return_value.stdout.read.side_effect = OSError
    with pytest.raises(OSError):
        shell._get_version()
    assert Popen.call_args[0][0] == ["bash", "-c", "echo $BASH_VERSION"]
