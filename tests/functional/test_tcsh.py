import pytest
from tests.functional.plots import (
    with_confirmation,
    without_confirmation,
    refuse_with_confirmation,
    select_command_with_arrows,
)

containers = (("thefuck/python3", "", "tcsh"), ("thefuck/python2", "", "tcsh"))


@pytest.fixture(params=containers)
def proc(request, spawnu, TIMEOUT):
    proc = spawnu(*request.param)
    proc.sendline("tcsh")
    proc.sendline("setenv PYTHONIOENCODING utf8")
    proc.sendline("eval `thefuck --alias`")
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
