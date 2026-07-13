from __future__ import annotations

from itertools import islice
from collections.abc import Callable

import pytest

from thefuck import const, ui
from thefuck.conf import Settings
from thefuck.types import CorrectedCommand


@pytest.fixture
def patch_get_key(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[list[str | const._GenConst]], None]:
    def patch(vals: list[str | const._GenConst]) -> None:
        iter_vals = iter(vals)
        monkeypatch.setattr("thefuck.ui.get_key", lambda: next(iter_vals))

    return patch


def test_read_actions(
    patch_get_key: Callable[[list[str | const._GenConst]], None],
) -> None:
    patch_get_key(
        [
            # Enter:
            "\n",
            # Enter:
            "\r",
            # Ignored:
            "x",
            "y",
            # Up:
            const.KEY_UP,
            "k",
            # Down:
            const.KEY_DOWN,
            "j",
            # Ctrl+C:
            const.KEY_CTRL_C,
            "q",
        ]
    )
    assert list(islice(ui.read_actions(), 8)) == [
        const.ACTION_SELECT,
        const.ACTION_SELECT,
        const.ACTION_PREVIOUS,
        const.ACTION_PREVIOUS,
        const.ACTION_NEXT,
        const.ACTION_NEXT,
        const.ACTION_ABORT,
        const.ACTION_ABORT,
    ]


def test_command_selector() -> None:
    selector = ui.CommandSelector(iter([1, 2, 3]))  # type: ignore[arg-type]
    assert selector.value == 1
    selector.next()
    assert selector.value == 2
    selector.next()
    assert selector.value == 3
    selector.next()
    assert selector.value == 1
    selector.previous()
    assert selector.value == 3


@pytest.fixture
def commands_with_side_effect() -> list[CorrectedCommand]:
    return [
        CorrectedCommand("ls", lambda *_: None, 100),
        CorrectedCommand("cd", lambda *_: None, 100),
    ]


@pytest.fixture
def commands() -> list[CorrectedCommand]:
    return [CorrectedCommand("ls", None, 100), CorrectedCommand("cd", None, 100)]


@pytest.mark.usefixtures("no_colors")
def test_without_commands(capsys: pytest.CaptureFixture) -> None:
    assert ui.select_command(iter([])) is None
    assert capsys.readouterr() == ("", "No fucks given\n")


@pytest.mark.usefixtures("no_colors")
def test_without_confirmation(
    capsys: pytest.CaptureFixture, commands: list[CorrectedCommand], settings
) -> None:
    settings.require_confirmation = False
    assert ui.select_command(iter(commands)) == commands[0]
    assert capsys.readouterr() == ("", const.USER_COMMAND_MARK + "ls\n")


@pytest.mark.usefixtures("no_colors")
def test_without_confirmation_with_side_effects(
    capsys: pytest.CaptureFixture,
    commands_with_side_effect: list[CorrectedCommand],
    settings: Settings,
) -> None:
    settings.require_confirmation = False
    assert (
        ui.select_command(iter(commands_with_side_effect))
        == commands_with_side_effect[0]
    )
    assert capsys.readouterr() == (
        "",
        const.USER_COMMAND_MARK + "ls (+side effect)\n",
    )


@pytest.mark.usefixtures("no_colors")
def test_with_confirmation(
    capsys: pytest.CaptureFixture,
    patch_get_key: Callable[[list[str | const._GenConst]], None],
    commands: list[CorrectedCommand],
) -> None:
    patch_get_key(["\n"])
    assert ui.select_command(iter(commands)) == commands[0]
    assert capsys.readouterr() == (
        "",
        const.USER_COMMAND_MARK + "\x1b[1K\rls [enter/↑/↓/ctrl+c]\n",
    )


@pytest.mark.usefixtures("no_colors")
def test_with_confirmation_abort(
    capsys: pytest.CaptureFixture,
    patch_get_key: Callable[[list[str | const._GenConst]], None],
    commands: list[CorrectedCommand],
) -> None:
    patch_get_key([const.KEY_CTRL_C])
    assert ui.select_command(iter(commands)) is None
    assert capsys.readouterr() == (
        "",
        const.USER_COMMAND_MARK + "\x1b[1K\rls [enter/↑/↓/ctrl+c]\nAborted\n",
    )


@pytest.mark.usefixtures("no_colors")
def test_with_confirmation_with_side_effct(
    capsys: pytest.CaptureFixture,
    patch_get_key: Callable[[list[str | const._GenConst]], None],
    commands_with_side_effect: list[CorrectedCommand],
) -> None:
    patch_get_key(["\n"])
    assert (
        ui.select_command(iter(commands_with_side_effect))
        == commands_with_side_effect[0]
    )
    assert capsys.readouterr() == (
        "",
        const.USER_COMMAND_MARK + "\x1b[1K\rls (+side effect) [enter/↑/↓/ctrl+c]\n",
    )


@pytest.mark.usefixtures("no_colors")
def test_with_confirmation_select_second(
    capsys: pytest.CaptureFixture,
    patch_get_key: Callable[[list[str | const._GenConst]], None],
    commands: list[CorrectedCommand],
) -> None:
    patch_get_key([const.KEY_DOWN, "\n"])
    assert ui.select_command(iter(commands)) == commands[1]
    stderr = f"{const.USER_COMMAND_MARK}\x1b[1K\rls [enter/↑/↓/ctrl+c]{const.USER_COMMAND_MARK}\x1b[1K\rcd [enter/↑/↓/ctrl+c]\n"
    assert capsys.readouterr() == ("", stderr)
