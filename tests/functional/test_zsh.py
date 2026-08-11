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


init_zshrc = """echo '
export SHELL=/usr/bin/zsh
export HISTFILE=~/.zsh_history
echo > $HISTFILE
export SAVEHIST=100
export HISTSIZE=100
eval $(thefuck --alias {})
setopt INC_APPEND_HISTORY
echo "instant mode ready: $THEFUCK_INSTANT_MODE"
' > ~/.zshrc"""


@pytest.fixture(params=[False, True])
def proc(request, spawnu, TIMEOUT):
    instant_mode = request.param
    proc = spawnu("thefuck/python3", "", "sh")
    proc.sendline(
        init_zshrc.format("--enable-experimental-instant-mode" if instant_mode else "")
    )
    proc.sendline("zsh")
    if instant_mode:
        assert proc.expect([TIMEOUT, "instant mode ready: True"])
    return proc


@pytest.mark.functional
def test_with_confirmation(proc, TIMEOUT) -> None:
    with_confirmation(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "echo test")


@pytest.mark.functional
def test_select_command_with_arrows(proc, TIMEOUT) -> None:
    select_command_with_arrows(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "git help", "git hook")


@pytest.mark.functional
def test_refuse_with_confirmation(proc, TIMEOUT) -> None:
    refuse_with_confirmation(proc, TIMEOUT)
    history_not_changed(proc, TIMEOUT)


@pytest.mark.functional
def test_without_confirmation(proc, TIMEOUT) -> None:
    without_confirmation(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "echo test")


@pytest.mark.functional
def test_how_to_configure_alias(proc, TIMEOUT) -> None:
    proc.sendline("unfunction fuck")
    how_to_configure(proc, TIMEOUT)
