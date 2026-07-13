from __future__ import annotations

from typing import Any

import pytest
import pytest_mock

from thefuck.shells import Powershell


@pytest.fixture
def shell() -> Powershell:
    return Powershell()


@pytest.fixture(autouse=True)
def Popen(mocker) -> pytest_mock.MockType:
    return mocker.patch("thefuck.shells.powershell.Popen")


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_and_(shell: Powershell) -> None:
    assert shell.and_("ls", "cd") == "(ls) -and (cd)"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias(shell: Powershell) -> None:
    assert "function fuck" in shell.app_alias("fuck")
    assert "function FUCK" in shell.app_alias("FUCK")
    assert "thefuck" in shell.app_alias("fuck")


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure(shell: Powershell) -> None:
    assert not shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "side_effect, expected_version, call_args",
    [
        (
            [
                b"""Major  Minor  Build  Revision
-----  -----  -----  --------
5      1      17763  316     \n"""
            ],
            "PowerShell 5.1.17763.316",
            ["powershell.exe"],
        ),
        (
            [IOError, b"PowerShell 6.1.2\n"],
            "PowerShell 6.1.2",
            ["powershell.exe", "pwsh"],
        ),
    ],
)
def test_info(
    side_effect: Any,
    expected_version: str,
    call_args: list[str],
    shell: Powershell,
    Popen: pytest_mock.MockType,
) -> None:
    Popen.return_value.stdout.read.side_effect = side_effect
    assert shell.info() == expected_version
    assert Popen.call_count == len(call_args)
    assert all(
        Popen.call_args_list[i][0][0][0] == call_arg
        for i, call_arg in enumerate(call_args)
    )


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_version_error(shell: Powershell, Popen: pytest_mock.MockType) -> None:
    Popen.return_value.stdout.read.side_effect = RuntimeError
    with pytest.raises(RuntimeError):
        shell._get_version()
    assert Popen.call_args[0][0] == ["powershell.exe", "$PSVersionTable.PSVersion"]
