from __future__ import annotations

import sys
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest
from psutil import AccessDenied, TimeoutExpired

from thefuck.output_readers import rerun


@pytest.fixture
def proc_mock() -> Generator[Mock]:
    patcher = patch("thefuck.output_readers.rerun.Process")
    process_mock = patcher.start()
    _proc_mock = process_mock.return_value = Mock()
    try:
        yield _proc_mock
    finally:
        patcher.stop()


@patch("thefuck.output_readers.rerun._wait_output", return_value=False)
@patch("thefuck.output_readers.rerun.Popen")
def test_get_output(popen_mock: Mock, wait_output_mock: Mock) -> None:
    popen_mock.return_value.stdout.read.return_value = b"output"
    assert rerun.get_output("", "") is None
    wait_output_mock.assert_called_once()


@patch("thefuck.output_readers.rerun.Popen")
def test_get_output_invalid_continuation_byte(popen_mock: Mock) -> None:
    output = b"ls: illegal option -- \xc3\nusage: ls [-@ABC...] [file ...]\n"
    expected = "ls: illegal option -- \ufffd\nusage: ls [-@ABC...] [file ...]\n"
    popen_mock.return_value.stdout.read.return_value = output
    actual = rerun.get_output("", "")
    assert actual == expected


@pytest.mark.skipif(sys.platform == "win32", reason="skip when running on Windows")
@patch("thefuck.output_readers.rerun._wait_output")
def test_get_output_unicode_misspell(wait_output_mock: Mock) -> None:
    rerun.get_output("pácman", "pácman")
    wait_output_mock.assert_called_once()


def test_wait_output_is_slow(proc_mock: Mock, settings: Any) -> None:
    assert rerun._wait_output(Mock(), True)
    proc_mock.wait.assert_called_once_with(settings.wait_slow_command)


def test_wait_output_is_not_slow(proc_mock: Mock, settings: Any) -> None:
    assert rerun._wait_output(Mock(), False)
    proc_mock.wait.assert_called_once_with(settings.wait_command)


@patch("thefuck.output_readers.rerun._kill_process")
def test_wait_output_timeout(proc_mock: Mock, kill_process_mock: Mock) -> None:
    proc_mock.wait.side_effect = TimeoutExpired(3)
    proc_mock.children.return_value = []
    assert not rerun._wait_output(Mock(), False)
    kill_process_mock.assert_called_once_with(proc_mock)


@patch("thefuck.output_readers.rerun._kill_process")
def test_wait_output_timeout_children(proc_mock: Mock, kill_process_mock: Mock) -> None:
    proc_mock.wait.side_effect = TimeoutExpired(3)
    proc_mock.children.return_value = [Mock()] * 2
    assert not rerun._wait_output(Mock(), False)
    assert kill_process_mock.call_count == 3


def test_kill_process() -> None:
    proc = Mock()
    rerun._kill_process(proc)
    proc.kill.assert_called_once_with()


@patch("thefuck.output_readers.rerun.logs")
def test_kill_process_access_denied(logs_mock: Mock) -> None:
    proc = Mock()
    proc.kill.side_effect = AccessDenied()
    rerun._kill_process(proc)
    proc.kill.assert_called_once_with()
    logs_mock.debug.assert_called_once()
