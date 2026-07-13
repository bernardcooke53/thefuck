from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
import pytest_mock

from thefuck.conf import Settings
from thefuck.const import ARGUMENT_PLACEHOLDER
from thefuck.shells import Fish


@pytest.fixture
def shell():
    return Fish()


@pytest.fixture(autouse=True)
def Popen(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    mock = mocker.patch("thefuck.shells.fish.Popen")
    mock.return_value.stdout.read.side_effect = [
        (
            b"cd\nfish_config\nfuck\nfunced\nfuncsave\ngrep\nhistory\nll\nls\n"
            b"man\nmath\npopd\npushd\nruby"
        ),
        (
            b"alias fish_key_reader /usr/bin/fish_key_reader\nalias g git\n"
            b"alias alias_with_equal_sign=echo\ninvalid_alias"
        ),
        b"func1\nfunc2",
        b"",
    ]
    return mock


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "key, value",
    [
        ("TF_OVERRIDDEN_ALIASES", "cut,git,sed"),  # legacy
        ("THEFUCK_OVERRIDDEN_ALIASES", "cut,git,sed"),
        ("THEFUCK_OVERRIDDEN_ALIASES", "cut, git, sed"),
        ("THEFUCK_OVERRIDDEN_ALIASES", " cut,\tgit,sed\n"),
        ("THEFUCK_OVERRIDDEN_ALIASES", "\ncut,\n\ngit,\tsed\r"),
    ],
)
def test_get_overridden_aliases(
    shell: Fish, os_environ: dict[str, Any], key: str, value: str
) -> None:
    os_environ[key] = value
    overridden = shell._get_overridden_aliases()
    assert set(overridden) == {
        "cd",
        "cut",
        "git",
        "grep",
        "ls",
        "man",
        "open",
        "sed",
    }


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "before, after",
    [
        ("cd", "cd"),
        ("pwd", "pwd"),
        ("fuck", 'fish -ic "fuck"'),
        ("find", "find"),
        ("funced", 'fish -ic "funced"'),
        ("grep", "grep"),
        ("awk", "awk"),
        ('math "2 + 2"', r'fish -ic "math \"2 + 2\""'),
        ("man", "man"),
        ("open", "open"),
        ("vim", "vim"),
        ("ll", 'fish -ic "ll"'),
        ("ls", "ls"),
        ("g", "git"),
    ],
)
def test_from_shell(before: str, after: str, shell: Fish) -> None:
    assert shell.from_shell(before) == after


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_to_shell(shell: Fish) -> None:
    assert shell.to_shell("pwd") == "pwd"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_and_(shell: Fish) -> None:
    assert shell.and_("foo", "bar") == "foo; and bar"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_or_(shell: Fish) -> None:
    assert shell.or_("foo", "bar") == "foo; or bar"


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_aliases(shell: Fish) -> None:
    assert shell.get_aliases() == {
        "fish_config": "fish_config",
        "fuck": "fuck",
        "funced": "funced",
        "funcsave": "funcsave",
        "history": "history",
        "ll": "ll",
        "math": "math",
        "popd": "popd",
        "pushd": "pushd",
        "ruby": "ruby",
        "g": "git",
        "fish_key_reader": "/usr/bin/fish_key_reader",
        "alias_with_equal_sign": "echo",
    }
    assert shell.get_aliases() == {"func1": "func1", "func2": "func2"}


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias(shell: Fish) -> None:
    assert "function fuck" in shell.app_alias("fuck")
    assert "function FUCK" in shell.app_alias("FUCK")
    assert "thefuck" in shell.app_alias("fuck")
    assert "TF_SHELL=fish" in shell.app_alias("fuck")
    assert "TF_ALIAS=fuck PYTHONIOENCODING" in shell.app_alias("fuck")
    assert "PYTHONIOENCODING=utf-8 thefuck" in shell.app_alias("fuck")
    assert ARGUMENT_PLACEHOLDER in shell.app_alias("fuck")


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_app_alias_alter_history(settings: Settings, shell: Fish) -> None:
    settings.alter_history = True
    assert (
        "builtin history delete --exact --case-sensitive -- $fucked_up_command\n"
        in shell.app_alias("FUCK")
    )
    assert "builtin history merge\n" in shell.app_alias("FUCK")
    settings.alter_history = False
    assert "builtin history delete" not in shell.app_alias("FUCK")
    assert "builtin history merge" not in shell.app_alias("FUCK")


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_history(history_lines: Callable[[list[str]], None], shell: Fish) -> None:
    history_lines(
        ["- cmd: ls", "  when: 1432613911", "- cmd: rm", "  when: 1432613916"]
    )
    assert list(shell.get_history()) == ["ls", "rm"]


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "entry, entry_utf8",
    [
        ("ls", "- cmd: ls\n   when: 1430707243\n"),
        ("echo café", "- cmd: echo café\n   when: 1430707243\n"),
    ],
)
def test_put_to_history(
    entry: str,
    entry_utf8: str,
    builtins_open: pytest_mock.MockType,
    mocker: pytest_mock.MockerFixture,
    shell: Fish,
) -> None:
    mocker.patch("thefuck.shells.fish.time", return_value=1430707243.3517463)
    shell.put_to_history(entry)
    builtins_open.return_value.__enter__.return_value.write.assert_called_once_with(
        entry_utf8
    )


def test_how_to_configure(shell: Fish, config_exists) -> None:
    config_exists.return_value = True
    assert shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_how_to_configure_when_config_not_found(shell: Fish, config_exists: Any):
    config_exists.return_value = False
    assert not shell.how_to_configure().can_configure_automatically


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
def test_get_version(shell: Fish, Popen: pytest_mock.MockType) -> None:
    Popen.return_value.stdout.read.side_effect = [b"fish, version 3.5.9\n"]
    assert shell._get_version() == "3.5.9"
    assert Popen.call_args[0][0] == ["fish", "--version"]


@pytest.mark.usefixtures("isfile", "no_memoize", "no_cache")
@pytest.mark.parametrize(
    "side_effect, exception",
    [
        ([b"\n"], IndexError),
        (OSError("file not found"), OSError),
    ],
)
def test_get_version_error(
    side_effect: Any,
    exception: type[Exception],
    shell: Fish,
    Popen: pytest_mock.MockType,
) -> None:
    Popen.return_value.stdout.read.side_effect = side_effect
    with pytest.raises(exception):
        shell._get_version()
    assert Popen.call_args[0][0] == ["fish", "--version"]
