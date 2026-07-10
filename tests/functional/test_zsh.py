import pytest
from tests.functional.plots import (
    with_confirmation,
    without_confirmation,
    refuse_with_confirmation,
    history_changed,
    history_not_changed,
    select_command_with_arrows,
    how_to_configure,
)


python_3 = ("thefuck/python3", "", "sh")
python_2 = ("thefuck/python2", "", "sh")


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


@pytest.fixture(params=[(python_3, False), (python_3, True), (python_2, False)])
def proc(request, spawnu, TIMEOUT):
    container, instant_mode = request.param
    proc = spawnu(*container)
    proc.sendline(
        init_zshrc.format("--enable-experimental-instant-mode" if instant_mode else "")
    )
    proc.sendline("zsh")
    if instant_mode:
        assert proc.expect([TIMEOUT, "instant mode ready: True"])
    return proc


@pytest.mark.functional
def test_with_confirmation(proc, TIMEOUT):
    with_confirmation(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "echo test")


@pytest.mark.functional
def test_select_command_with_arrows(proc, TIMEOUT):
    select_command_with_arrows(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "git help", "git hook")


@pytest.mark.functional
def test_refuse_with_confirmation(proc, TIMEOUT):
    refuse_with_confirmation(proc, TIMEOUT)
    history_not_changed(proc, TIMEOUT)


@pytest.mark.functional
def test_without_confirmation(proc, TIMEOUT):
    without_confirmation(proc, TIMEOUT)
    history_changed(proc, TIMEOUT, "echo test")


@pytest.mark.functional
def test_how_to_configure_alias(proc, TIMEOUT):
    proc.sendline("unfunction fuck")
    how_to_configure(proc, TIMEOUT)
