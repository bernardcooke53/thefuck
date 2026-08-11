from __future__ import annotations

from pathlib import Path
from typing import Sequence, Callable

import pytest
import pytest_mock

from thefuck import const, corrector
from thefuck.conf import Settings
from thefuck.corrector import get_corrected_commands, organize_commands
from thefuck.types import Command

from tests.utils import CorrectedCommand, Rule


@pytest.fixture
def glob(mocker: pytest_mock.MockerFixture) -> Callable[[list[Path]], None]:
    results = {}
    mocker.patch(
        "pathlib.Path.glob",
        new_callable=lambda: lambda *_: results.pop("value", []),
    )
    return lambda value: results.update({"value": value})


@pytest.fixture(autouse=True)
def load_source(monkeypatch) -> None:
    monkeypatch.setattr("thefuck.types.load_source", lambda x, _: Rule(x))


def _compare_names(rules, names: Sequence[str]) -> None:
    assert {r.name for r in rules} == set(names)


@pytest.mark.parametrize(
    "paths, conf_rules, exclude_rules, loaded_rules",
    [
        (["git.py", "bash.py"], const.DEFAULT_RULES, [], ["git", "bash"]),
        (["git.py", "bash.py"], ["git"], [], ["git"]),
        (["git.py", "bash.py"], const.DEFAULT_RULES, ["git"], ["bash"]),
        (["git.py", "bash.py"], ["git"], ["git"], []),
    ],
)
def test_get_rules(
    glob: Callable[[list[Path]], None],
    settings: Settings,
    paths: list[str],
    conf_rules: list[str],
    exclude_rules: list[str],
    loaded_rules: list[str],
) -> None:
    glob([Path(path) for path in paths])
    settings.update(rules=conf_rules, priority={}, exclude_rules=exclude_rules)
    rules = corrector.get_rules()
    _compare_names(rules, loaded_rules)


def test_get_rules_rule_exception(
    mocker: pytest_mock.MockerFixture, glob: Callable[[list[Path]], None]
) -> None:
    load_source = mocker.patch(
        "thefuck.types.load_source", side_effect=ImportError("No module named foo...")
    )
    glob([Path("git.py")])
    assert not corrector.get_rules()
    load_source.assert_called_once_with("git", "git.py")


def test_get_corrected_commands(mocker: pytest_mock.MockerFixture) -> None:
    command = Command("test", "test")
    rules = [
        Rule(match=lambda _: False),
        Rule(
            match=lambda _: True, get_new_command=lambda x: x.script + "!", priority=100
        ),
        Rule(
            match=lambda _: True,
            get_new_command=lambda x: [x.script + "@", x.script + ";"],
            priority=60,
        ),
    ]
    mocker.patch("thefuck.corrector.get_rules", return_value=rules)
    assert [cmd.script for cmd in get_corrected_commands(command)] == [
        "test!",
        "test@",
        "test;",
    ]


def test_organize_commands() -> None:
    """Ensures that the function removes duplicates and sorts commands."""
    commands = [
        CorrectedCommand("ls"),
        CorrectedCommand("ls -la", priority=9000),
        CorrectedCommand("ls -lh", priority=100),
        CorrectedCommand("echo café", priority=200),
        CorrectedCommand("ls -lh", priority=9999),
    ]
    assert list(organize_commands(iter(commands))) == [
        CorrectedCommand("ls"),
        CorrectedCommand("ls -lh", priority=100),
        CorrectedCommand("echo café", priority=200),
        CorrectedCommand("ls -la", priority=9000),
    ]
