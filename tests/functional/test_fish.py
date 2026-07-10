import pytest
from tests.functional.plots import (
    with_confirmation,
    without_confirmation,
    refuse_with_confirmation,
    select_command_with_arrows,
)

containers = (("thefuck/python3", "", "fish"), ("thefuck/python2", "", "fish"))


@pytest.fixture(params=containers)
def proc(request, spawnu, TIMEOUT):
    proc = spawnu(*request.param)
    proc.sendline("thefuck --alias > ~/.config/fish/config.fish")
    proc.sendline("fish")
    return proc


@pytest.mark.functional
def test_with_confirmation(proc, TIMEOUT):
    with_confirmation(proc, TIMEOUT)


@pytest.mark.functional
def test_select_command_with_arrows(proc, TIMEOUT):
    select_command_with_arrows(proc, TIMEOUT)


@pytest.mark.functional
def test_refuse_with_confirmation(proc, TIMEOUT):
    refuse_with_confirmation(proc, TIMEOUT)


@pytest.mark.functional
def test_without_confirmation(proc, TIMEOUT):
    without_confirmation(proc, TIMEOUT)


# TODO: ensure that history changes.
