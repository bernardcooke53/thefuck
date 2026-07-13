from __future__ import annotations
from typing import Any

import pytest
import pytest_mock
from pytest_docker_pexpect.docker import (
    run as pexpect_docker_run,
    stats as pexpect_docker_stats,
)

pytestmark = pytest.mark.functional


@pytest.fixture(autouse=True)
def build_container_mock(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    return mocker.patch("pytest_docker_pexpect.docker.build_container")


def run_side_effect(*args: Any, **kwargs: Any) -> str:
    container_id = pexpect_docker_run(*args, **kwargs)
    pexpect_docker_stats(container_id)
    return container_id


@pytest.fixture(autouse=True)
def run_mock(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    return mocker.patch("pytest_docker_pexpect.docker.run", side_effect=run_side_effect)
