from __future__ import annotations

import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

import pytest

from thefuck import conf, const, shells

shells.shell = shells.Generic()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Adds `--enable-functional` argument."""
    group = parser.getgroup("thefuck")
    group.addoption(
        "--enable-functional",
        action="store_true",
        default=False,
        help="Enable functional tests",
    )


@pytest.fixture(autouse=True)
def functional(request: pytest.FixtureRequest) -> None:
    if request.node.get_closest_marker("functional") and not request.config.getoption(
        "enable_functional"
    ):
        pytest.skip("functional tests are disabled")


@pytest.fixture
def no_memoize(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("thefuck.utils.memoize.disabled", True)


@pytest.fixture(autouse=True)
def settings() -> Generator[conf.Settings]:
    try:
        conf.settings.user_dir = Path("~/.thefuck")
        yield conf.settings
    finally:
        conf.settings.clear()
        conf.settings.update(const.DEFAULT_SETTINGS)


@pytest.fixture
def no_colors(settings: Any) -> None:
    settings.no_colors = True


@pytest.fixture(autouse=True)
def no_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("thefuck.utils.cache.disabled", True)


@pytest.fixture
def source_root() -> Path:
    return Path(__file__).parent.parent.resolve()


@pytest.fixture
def set_shell(monkeypatch: pytest.MonkeyPatch) -> Callable[..., None]:
    def _set(cls: Any) -> Any:
        shell = cls()
        monkeypatch.setattr("thefuck.shells.shell", shell)
        return shell

    return _set


@pytest.fixture(autouse=True)
def os_environ(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    env = {"PATH": os.environ["PATH"]}
    monkeypatch.setattr("os.environ", env)
    return env
