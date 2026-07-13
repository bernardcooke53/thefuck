from __future__ import annotations

from unittest.mock import Mock

import pytest
import pytest_mock

from thefuck.entrypoints.alias import _get_alias, print_alias


@pytest.mark.parametrize(
    "enable_experimental_instant_mode, which, is_instant",
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
    ],
)
def test_get_alias(
    monkeypatch: pytest.MonkeyPatch,
    mocker: pytest_mock.MockerFixture,
    enable_experimental_instant_mode: bool,
    which: bool,
    is_instant: bool,
) -> None:
    args = Mock(
        enable_experimental_instant_mode=enable_experimental_instant_mode,
        alias="fuck",
    )
    mocker.patch("shutil.which", return_value=which)
    shell = Mock(
        app_alias=lambda _: "app_alias",
        instant_mode_alias=lambda _: "instant_mode_alias",
    )
    monkeypatch.setattr("thefuck.entrypoints.alias.shell", shell)

    alias = _get_alias(args)
    if is_instant:
        assert alias == "instant_mode_alias"
    else:
        assert alias == "app_alias"


def test_print_alias(mocker: pytest_mock.MockerFixture) -> None:
    settings_mock = mocker.patch("thefuck.entrypoints.alias.settings")
    _get_alias_mock = mocker.patch("thefuck.entrypoints.alias._get_alias")
    known_args = Mock()
    print_alias(known_args)
    settings_mock.init.assert_called_once_with(known_args)
    _get_alias_mock.assert_called_once_with(known_args)
