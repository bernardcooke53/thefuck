from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from thefuck.entrypoints.fix_command import _get_raw_command


def test_from_force_command_argument() -> None:
    known_args = Mock(force_command="git brunch")
    assert _get_raw_command(known_args) == ["git brunch"]


def test_from_command_argument(os_environ: dict[str, Any]) -> None:
    os_environ["TF_HISTORY"] = None
    known_args = Mock(force_command=None, command=["sl"])
    assert _get_raw_command(known_args) == ["sl"]


@pytest.mark.parametrize(
    "history, result",
    [
        ("git br", "git br"),
        ("git br\nfcuk", "git br"),
        ("git br\nfcuk\nls", "ls"),
        ("git br\nfcuk\nls\nfuk", "ls"),
    ],
)
def test_from_history(os_environ: dict[str, str], history: str, result: str) -> None:
    os_environ["TF_HISTORY"] = history
    known_args = Mock(force_command=None, command=None)
    assert _get_raw_command(known_args) == [result]
