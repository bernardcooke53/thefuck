from __future__ import annotations

import pytest
import pytest_mock


@pytest.fixture
def builtins_open(mocker):
    return mocker.patch("builtins.open")


@pytest.fixture
def isfile(mocker: pytest_mock.MockerFixture):
    return mocker.patch("os.path.isfile", return_value=True)


@pytest.fixture
def history_lines(mocker: pytest_mock.MockerFixture, isfile: pytest_mock.MockType):
    def aux(lines):
        mock = mocker.patch("builtins.open")
        mock.return_value.__enter__.return_value.readlines.return_value = lines

    return aux


@pytest.fixture
def config_exists(mocker: pytest_mock.MockerFixture):
    path_mock = mocker.patch("thefuck.shells.generic.Path")
    return path_mock.return_value.expanduser.return_value.exists
