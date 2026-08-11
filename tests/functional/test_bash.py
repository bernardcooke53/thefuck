from __future__ import annotations

import pytest

from tests.functional.plots import (
    history_changed,
    history_not_changed,
    how_to_configure,
    refuse_with_confirmation,
    select_command_with_arrows,
    with_confirmation,
    without_confirmation,
)

pytestmark = pytest.mark.functional

init_bashrc = """echo '
export SHELL=/bin/bash
export PS1="$ "
echo > $HISTFILE
eval $(thefuck --alias {})
echo "instant mode ready: $THEFUCK_INSTANT_MODE"
' > ~/.bashrc"""


@pytest.fixture(params=[False, True])
def proc(request: pytest.FixtureRequest, spawnu, TIMEOUT):
    instant_mode = request.param
    proc = spawnu("thefuck/python3", "", "sh")
    proc.sendline(
        init_bashrc.format("--enable-experimental-instant-mode" if instant_mode else "")
    )
    proc.sendline("bash")
    if instant_mode:
        assert proc.expect([TIMEOUT, "instant mode ready: True"])
    return proc


def test_with_confirmation(proc, TIMEOUT) -> None:
    with_confirmation(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "echo test")


def test_select_command_with_arrows(proc, TIMEOUT) -> None:
    select_command_with_arrows(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "git help", "git hook")


def test_refuse_with_confirmation(proc, TIMEOUT) -> None:
    refuse_with_confirmation(proc, TIMEOUT)
    history_not_changed(proc, TIMEOUT)


def test_without_confirmation(proc, TIMEOUT) -> None:
    without_confirmation(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "echo test")


def test_how_to_configure_alias(proc, TIMEOUT) -> None:
    proc.sendline("unset -f fuck")
    how_to_configure(proc, TIMEOUT)
