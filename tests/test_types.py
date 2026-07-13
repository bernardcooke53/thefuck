from __future__ import annotations

import os
from pathlib import Path
from subprocess import PIPE, STDOUT
from typing import Any
from unittest.mock import Mock

import pytest
import pytest_mock

from thefuck import const
from thefuck.conf import Settings
from thefuck.exceptions import EmptyCommand
from thefuck.types import Command

from tests.utils import CorrectedCommand, Rule


def test_equality() -> None:
    assert CorrectedCommand("ls", None, 100) == CorrectedCommand("ls", None, 200)
    assert CorrectedCommand("ls", None, 100) != CorrectedCommand(
        "ls", lambda *_: _, 100
    )


def test_hashable() -> None:
    assert {
        CorrectedCommand("ls", None, 100),
        CorrectedCommand("ls", None, 200),
    } == {CorrectedCommand("ls")}


def test_representable() -> None:
    assert (
        "{}".format(CorrectedCommand("ls", None, 100))
        == "CorrectedCommand(script=ls, side_effect=None, priority=100)"
    )
    assert (
        "{}".format(CorrectedCommand("echo café", None, 100))
        == "CorrectedCommand(script=echo café, side_effect=None, priority=100)"
    )


@pytest.mark.parametrize(
    "script, printed, override_settings",
    [
        ("git branch", "git branch", {"repeat": False, "debug": False}),
        (
            "git brunch",
            "git brunch || fuck --repeat --force-command 'git brunch'",
            {"repeat": True, "debug": False},
        ),
        (
            "git brunch",
            "git brunch || fuck --repeat --debug --force-command 'git brunch'",
            {"repeat": True, "debug": True},
        ),
    ],
)
def test_run(
    capsys: pytest.CaptureFixture,
    settings: Settings,
    script: str,
    printed: str,
    override_settings: dict[str, Any],
) -> None:
    settings.update(override_settings)
    CorrectedCommand(script, None, 1000).run(Command(script, ""))
    out, _ = capsys.readouterr()
    assert out == printed


def test_from_path_rule_exception(mocker: pytest_mock.MockerFixture) -> None:
    load_source = mocker.patch(
        "thefuck.types.load_source",
        side_effect=ImportError("No module named foo..."),
    )
    assert Rule.from_path(Path("git.py")) is None
    load_source.assert_called_once_with("git", "git.py")


def test_from_path(mocker: pytest_mock.MockerFixture) -> None:
    match = object()
    get_new_command = object()
    load_source = mocker.patch(
        "thefuck.types.load_source",
        return_value=Mock(
            match=match,
            get_new_command=get_new_command,
            enabled_by_default=True,
            priority=900,
            requires_output=True,
        ),
    )
    rule_path = os.path.join(os.sep, "rules", "bash.py")
    assert Rule.from_path(Path(rule_path)) == Rule(
        "bash",
        match,  # type: ignore[arg-type]
        get_new_command,  # type: ignore[arg-type]
        priority=900,
    )
    load_source.assert_called_once_with("bash", rule_path)


def test_from_path_excluded_rule(mocker: pytest_mock.MockerFixture, settings) -> None:
    load_source = mocker.patch("thefuck.types.load_source")
    settings.update(exclude_rules=["git"])
    rule_path = os.path.join(os.sep, "rules", "git.py")
    assert Rule.from_path(Path(rule_path)) is None
    assert not load_source.called


@pytest.mark.parametrize(
    "rules, rule, is_enabled",
    [
        (const.DEFAULT_RULES, Rule("git", enabled_by_default=True), True),
        (const.DEFAULT_RULES, Rule("git", enabled_by_default=False), False),
        ([], Rule("git", enabled_by_default=False), False),
        ([], Rule("git", enabled_by_default=True), False),
        (
            const.DEFAULT_RULES + ["git"],
            Rule("git", enabled_by_default=False),
            True,
        ),
        (["git"], Rule("git", enabled_by_default=False), True),
    ],
)
def test_is_enabled(settings, rules, rule, is_enabled) -> None:
    settings.update(rules=rules)
    assert rule.is_enabled == is_enabled


def test_isnt_match() -> None:
    assert not Rule("", lambda _: False).is_match(Command("ls", ""))


def test_is_match() -> None:
    rule = Rule("", lambda x: x.script == "cd ..")
    assert rule.is_match(Command("cd ..", ""))


@pytest.mark.usefixtures("no_colors")
def test_isnt_match_when_rule_failed(capsys) -> None:
    rule = Rule("test", Mock(side_effect=OSError("Denied")), requires_output=False)
    assert not rule.is_match(Command("ls", ""))
    assert capsys.readouterr()[1].split("\n")[0] == "[WARN] Rule test:"


def test_get_corrected_commands_with_rule_returns_list() -> None:
    rule = Rule(
        get_new_command=lambda x: [x.script + "!", x.script + "@"], priority=100
    )
    assert list(rule.get_corrected_commands(Command("test", ""))) == [
        CorrectedCommand(script="test!", priority=100),
        CorrectedCommand(script="test@", priority=200),
    ]


def test_get_corrected_commands_with_rule_returns_command() -> None:
    rule = Rule(get_new_command=lambda x: x.script + "!", priority=100)
    assert list(rule.get_corrected_commands(Command("test", ""))) == [
        CorrectedCommand(script="test!", priority=100)
    ]


@pytest.fixture(autouse=True)
def Popen(monkeypatch) -> pytest_mock.MockType:
    Popen = Mock()
    Popen.return_value.stdout.read.return_value = b"output"
    monkeypatch.setattr("thefuck.output_readers.rerun.Popen", Popen)
    return Popen


@pytest.fixture(autouse=True)
def prepare(monkeypatch) -> None:
    monkeypatch.setattr("thefuck.output_readers.rerun._wait_output", lambda *_: True)


def test_from_script_calls(Popen, settings, os_environ) -> None:
    settings.env = {}
    assert Command.from_raw_script(["apt-get", "search", "vim"]) == Command(
        "apt-get search vim", "output"
    )
    Popen.assert_called_once_with(
        "apt-get search vim",
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
        env=os_environ,
    )


@pytest.mark.parametrize(
    "script, result",
    [
        ([], None),
        ([""], None),
        (["", ""], None),
        (["ls", "-la"], "ls -la"),
        (["ls"], "ls"),
        (["echo \\ "], "echo \\ "),
        (["echo \\\n"], "echo \\\n"),
    ],
)
def test_from_script(script, result) -> None:
    if result:
        assert Command.from_raw_script(script).script == result
    else:
        with pytest.raises(EmptyCommand):
            Command.from_raw_script(script)
