from __future__ import annotations

import pytest

from thefuck import logs
from thefuck.conf import Settings


def test_color(settings: Settings) -> None:
    settings.no_colors = False
    assert logs.color("red") == "red"
    settings.no_colors = True
    assert logs.color("red") == ""


@pytest.mark.usefixtures("no_colors")
@pytest.mark.parametrize("debug, stderr", [(True, "DEBUG: test\n"), (False, "")])
def test_debug(
    capsys: pytest.CaptureFixture, settings: Settings, debug: bool, stderr: str
) -> None:
    settings.debug = debug
    logs.debug("test")
    assert capsys.readouterr() == ("", stderr)
