from __future__ import annotations

from collections.abc import Callable, Generator
import warnings
from typing import Any
from unittest.mock import Mock, call, patch

import pytest
import pytest_mock

from thefuck.conf import Settings
from thefuck.types import Command
from thefuck.utils import (
    _cache,
    cache,
    default_settings,
    for_app,
    get_all_executables,
    get_all_matched_commands,
    get_close_matches,
    get_closest,
    get_valid_history_without_current,
    is_app,
    memoize,
    replace_argument,
)


@pytest.mark.parametrize(
    "override, old, new",
    [
        ({"key": "val"}, {}, {"key": "val"}),
        ({"key": "new-val"}, {"key": "val"}, {"key": "val"}),
        (
            {"key": "new-val", "unset": "unset"},
            {"key": "val"},
            {"key": "val", "unset": "unset"},
        ),
    ],
)
def test_default_settings(
    settings: Settings,
    override: dict[str, str],
    old: dict[str, str],
    new: dict[str, str],
) -> None:
    settings.clear()
    settings.update(old)
    default_settings(override)(lambda _: _)(None)
    assert settings == new


def test_memoize() -> None:
    fn = Mock(__name__="fn")
    memoized = memoize(fn)
    memoized()
    memoized()
    fn.assert_called_once_with()


@pytest.mark.usefixtures("no_memoize")
def test_no_memoize() -> None:
    fn = Mock(__name__="fn")
    memoized = memoize(fn)
    memoized()
    memoized()
    assert fn.call_count == 2


def test_when_can_match() -> None:
    assert get_closest("brnch", ["branch", "status"]) == "branch"


def test_when_cant_match() -> None:
    assert get_closest("st", ["status", "reset"]) == "status"


def test_without_fallback() -> None:
    assert get_closest("st", ["status", "reset"], fallback_to_first=False) is None


@patch("thefuck.utils.difflib_get_close_matches")
def test_call_with_n(difflib_mock: Mock) -> None:
    get_close_matches("", [], 1)
    assert difflib_mock.call_args[0][2] == 1


@patch("thefuck.utils.difflib_get_close_matches")
def test_call_without_n(difflib_mock: Mock, settings: Settings) -> None:
    get_close_matches("", [])
    assert difflib_mock.call_args[0][2] == settings.get("num_close_matches")


@pytest.fixture
def get_aliases(mocker: pytest_mock.MockerFixture) -> None:
    mocker.patch(
        "thefuck.shells.shell.get_aliases",
        return_value=["vim", "apt-get", "fsck", "fuck"],
    )


@pytest.mark.usefixtures("no_memoize", "get_aliases")
def test_get_all_executables() -> None:
    all_callables = get_all_executables()
    assert "vim" in all_callables
    assert "fsck" in all_callables
    assert "fuck" not in all_callables


@pytest.fixture
def os_environ_pathsep(
    monkeypatch: pytest.MonkeyPatch, path: str, pathsep: str
) -> dict[str, str]:
    env = {"PATH": path}
    monkeypatch.setattr("os.environ", env)
    monkeypatch.setattr("os.pathsep", pathsep)
    return env


@pytest.mark.usefixtures("no_memoize", "os_environ_pathsep")
@pytest.mark.parametrize(
    "path, pathsep",
    [("/foo:/bar:/baz:/foo/bar", ":"), (r"C:\\foo;C:\\bar;C:\\baz;C:\\foo\\bar", ";")],
)
def test_get_all_executables_pathsep(path: str, pathsep: str) -> None:
    with patch("thefuck.utils.Path") as Path_mock:
        get_all_executables()
        Path_mock.assert_has_calls([call(p) for p in path.split(pathsep)], True)


@pytest.mark.usefixtures("no_memoize", "os_environ_pathsep")
@pytest.mark.parametrize(
    "path, pathsep, excluded",
    [
        ("/foo:/bar:/baz:/foo/bar:/mnt/foo", ":", "/mnt/foo"),
        (r"C:\\foo;C:\\bar;C:\\baz;C:\\foo\\bar;Z:\\foo", ";", r"Z:\\foo"),
    ],
)
def test_get_all_executables_exclude_paths(
    path: str, pathsep: str, excluded: str, settings: Settings
) -> None:
    settings.init()
    settings.excluded_search_path_prefixes = [excluded]
    with patch("thefuck.utils.Path") as Path_mock:
        get_all_executables()
        path_list = path.split(pathsep)
        assert call(path_list[-1]) not in Path_mock.mock_calls
        assert all(call(p) in Path_mock.mock_calls for p in path_list[:-1])


@pytest.mark.parametrize(
    "args, result",
    [
        (("apt-get instol vim", "instol", "install"), "apt-get install vim"),
        (("git brnch", "brnch", "branch"), "git branch"),
    ],
)
def test_replace_argument(args: tuple[str, ...], result: str) -> None:
    assert replace_argument(*args) == result


@pytest.mark.parametrize(
    "stderr, result",
    [
        (
            (
                "git: 'cone' is not a git command. See 'git --help'.\n"
                "\n"
                "Did you mean one of these?\n"
                "\tclone"
            ),
            ["clone"],
        ),
        (
            (
                "git: 're' is not a git command. See 'git --help'.\n"
                "\n"
                "Did you mean one of these?\n"
                "\trebase\n"
                "\treset\n"
                "\tgrep\n"
                "\trm"
            ),
            ["rebase", "reset", "grep", "rm"],
        ),
        (
            (
                'tsuru: "target" is not a tsuru command. See "tsuru help".\n'
                "\n"
                "Did you mean one of these?\n"
                "\tservice-add\n"
                "\tservice-bind\n"
                "\tservice-doc\n"
                "\tservice-info\n"
                "\tservice-list\n"
                "\tservice-remove\n"
                "\tservice-status\n"
                "\tservice-unbind"
            ),
            [
                "service-add",
                "service-bind",
                "service-doc",
                "service-info",
                "service-list",
                "service-remove",
                "service-status",
                "service-unbind",
            ],
        ),
    ],
)
def test_get_all_matched_commands(stderr: str, result: list[str]) -> None:
    assert list(get_all_matched_commands(stderr)) == result


@pytest.mark.usefixtures("no_memoize")
@pytest.mark.parametrize(
    "script, names, result",
    [
        ("/usr/bin/git diff", ["git", "hub"], True),
        ("/bin/hdfs dfs -rm foo", ["hdfs"], True),
        ("git diff", ["git", "hub"], True),
        ("hub diff", ["git", "hub"], True),
        ("hg diff", ["git", "hub"], False),
    ],
)
def test_is_app(script: str, names: list[str], result: bool) -> None:
    assert is_app(Command(script, ""), *names) == result


@pytest.mark.usefixtures("no_memoize")
@pytest.mark.parametrize(
    "script, names, result",
    [
        ("/usr/bin/git diff", ["git", "hub"], True),
        ("/bin/hdfs dfs -rm foo", ["hdfs"], True),
        ("git diff", ["git", "hub"], True),
        ("hub diff", ["git", "hub"], True),
        ("hg diff", ["git", "hub"], False),
    ],
)
def test_for_app(script: str, names: list[str], result: bool) -> None:
    @for_app(*names)
    def match(command: str) -> bool:
        return True

    assert match(Command(script, "")) == result


@pytest.fixture
def shelve(mocker: pytest_mock.MockerFixture) -> dict[str, Any]:
    value = {}

    class _Shelve:
        def __init__(self) -> None:
            pass

        def __setitem__(self, k: str, v: Any) -> None:
            value[k] = v

        def __getitem__(self, k: str):
            return value[k]

        def get(self, k: str, v: Any | None = None) -> Any:
            return value.get(k, v)

        def close(self) -> None:
            return

    mocker.patch("thefuck.utils.shelve.open", new_callable=lambda: _Shelve)
    return value


@pytest.fixture(autouse=True)
def enable_cache(monkeypatch, shelve: dict[str, Any]) -> None:
    monkeypatch.setattr("thefuck.utils.cache.disabled", False)
    _cache._init_db()


@pytest.fixture(autouse=True)
def mtime(mocker: pytest_mock.MockerFixture) -> None:
    mocker.patch("thefuck.utils.os.path.getmtime", return_value=0)


@pytest.fixture
def fn() -> Callable[[], str]:
    @cache("~/.bashrc")
    def fn() -> str:
        return "test"

    return fn


@pytest.fixture
def key(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setattr("thefuck.utils.Cache._get_key", lambda *_: "key")
    return "key"


def test_with_blank_cache(
    shelve: dict[str, Any], fn: Callable[[], str], key: str
) -> None:
    assert shelve == {}
    assert fn() == "test"
    assert shelve == {key: {"etag": "0", "value": "test"}}


def test_with_filled_cache(
    shelve: dict[str, Any], fn: Callable[[], str], key: str
) -> None:
    cache_value = {key: {"etag": "0", "value": "new-value"}}
    shelve.update(cache_value)
    assert fn() == "new-value"
    assert shelve == cache_value


def test_when_etag_changed(
    shelve: dict[str, Any], fn: Callable[[], str], key: str
) -> None:
    shelve.update({key: {"etag": "-1", "value": "old-value"}})
    assert fn() == "test"
    assert shelve == {key: {"etag": "0", "value": "test"}}


@pytest.fixture(autouse=True)
def fail_on_warning() -> Generator[None]:
    warnings.simplefilter("error")
    yield
    warnings.resetwarnings()


@pytest.fixture(autouse=True)
def history(mocker: pytest_mock.MockerFixture) -> pytest_mock.MockType:
    mock = mocker.patch("thefuck.shells.shell.get_history")
    #  Passing as an argument causes `UnicodeDecodeError`
    #  with newer pytest and python 2.7
    mock.return_value = [
        "le cat",
        "fuck",
        "ls cat",
        "diff x",
        "nocommand x",
        "café ô",
    ]
    return mock


@pytest.fixture(autouse=True)
def alias(mocker: pytest_mock.MockerFixture):
    return mocker.patch("thefuck.utils.get_alias", return_value="fuck")


@pytest.fixture(autouse=True)
def bins(mocker: pytest_mock.MockerFixture):
    callables = []
    for name in ["diff", "ls", "café"]:
        bin_mock = mocker.Mock(name=name)
        bin_mock.configure_mock(name=name, is_dir=lambda: False)
        callables.append(bin_mock)
    path_mock = mocker.Mock(iterdir=mocker.Mock(return_value=callables))
    return mocker.patch("thefuck.utils.Path", return_value=path_mock)


@pytest.mark.parametrize(
    "script, result",
    [
        ("le cat", ["ls cat", "diff x", "café ô"]),
        ("diff x", ["ls cat", "café ô"]),
        ("fuck", ["ls cat", "diff x", "café ô"]),
        ("cafe ô", ["ls cat", "diff x", "café ô"]),
    ],
)
def test_get_valid_history_without_current(script: str, result: list[str]) -> None:
    command = Command(script, "")
    assert get_valid_history_without_current(command) == result
