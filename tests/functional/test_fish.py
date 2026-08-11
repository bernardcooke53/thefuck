from __future__ import annotations

import pytest

from tests.functional.plots import (
    refuse_with_confirmation,
    select_command_with_arrows,
    with_confirmation,
    without_confirmation,
)


@pytest.fixture
def proc(spawnu, TIMEOUT):
    proc = spawnu("thefuck/python3", "", "fish")
    proc.sendline("thefuck --alias > ~/.config/fish/config.fish")
    proc.sendline("fish")
    return proc


@pytest.mark.functional
def test_with_confirmation(proc, TIMEOUT) -> None:
    with_confirmation(proc, TIMEOUT)


@pytest.mark.functional
def test_select_command_with_arrows(proc, TIMEOUT) -> None:
    select_command_with_arrows(proc, TIMEOUT)


@pytest.mark.functional
def test_refuse_with_confirmation(proc, TIMEOUT) -> None:
    refuse_with_confirmation(proc, TIMEOUT)


@pytest.mark.functional
def test_without_confirmation(proc, TIMEOUT) -> None:
    without_confirmation(proc, TIMEOUT)


# TODO: ensure that history changes.
