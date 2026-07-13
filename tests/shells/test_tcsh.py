from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
import pytest_mock

from thefuck.shells.tcsh import Tcsh


@pytest.fixture
def shell() -> Tcsh:
    return Tcsh()


@pytest.fixture(autouse=True)
def Popen(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    mock = mocker.patch("thefuck.shells.tcsh.Popen")
    mock.return_value.stdout.read.return_value = (
        b"fuck\teval $(thefuck $(fc -ln -1))\nl\tls -CF\nla\tls -A\nll\tls -alF"
    )
    return mock


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
def test_from_shell(before: str, after: str, shell: Tcsh) -> None:
    assert shell.from_shell(before) == after


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_to_shell(shell: Tcsh) -> None:
    assert shell.to_shell("pwd") == "pwd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_and_(shell: Tcsh) -> None:
    assert shell.and_("ls", "cd") == "ls && cd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_or_(shell: Tcsh) -> None:
    assert shell.or_("ls", "cd") == "ls || cd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_aliases(shell: Tcsh) -> None:
    assert shell.get_aliases() == {
        "fuck": "eval $(thefuck $(fc -ln -1))",
        "l": "ls -CF",
        "la": "ls -A",
        "ll": "ls -alF",
    }


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias(shell: Tcsh) -> None:
    assert "setenv TF_SHELL tcsh" in shell.app_alias("fuck")
    assert "alias fuck" in shell.app_alias("fuck")
    assert "alias FUCK" in shell.app_alias("FUCK")
    assert "thefuck" in shell.app_alias("fuck")


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_history(history_lines: Callable[[list[str]], None], shell: Tcsh) -> None:
    history_lines(["ls", "rm"])
    assert list(shell.get_history()) == ["ls", "rm"]


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure(shell: Tcsh, config_exists: pytest_mock.MockType):
    config_exists.return_value = True
    assert shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure_when_config_not_found(
    shell: Tcsh, config_exists: pytest_mock.MockType
):
    config_exists.return_value = False
    assert not shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_info(shell: Tcsh, Popen: pytest_mock.MockType) -> None:
    Popen.return_value.stdout.read.side_effect = [
        b"tcsh 6.20.00 (Astron) 2016-11-24 (unknown-unknown-bsd44) \n"
    ]
    assert shell.info() == "Tcsh 6.20.00"
    assert Popen.call_args[0][0] == ["tcsh", "--version"]


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "side_effect, exception", [([b"\n"], IndexError), (OSError, OSError)]
)
def test_get_version_error(
    side_effect: Any,
    exception: type[Exception],
    shell: Tcsh,
    Popen: pytest_mock.MockType,
) -> None:
    Popen.return_value.stdout.read.side_effect = side_effect
    with pytest.raises(exception):
        shell._get_version()
    assert Popen.call_args[0][0] == ["tcsh", "--version"]
