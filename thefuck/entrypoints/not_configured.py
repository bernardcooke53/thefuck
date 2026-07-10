# Initialize output before importing any module, that can use colorama.
from __future__ import annotations

from pathlib import Path

from thefuck.system import init_output

init_output()

import getpass  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
from tempfile import gettempdir  # noqa: E402

from psutil import Process  # noqa: E402

from thefuck import const, logs  # noqa: E402
from thefuck.conf import settings  # noqa: E402
from thefuck.shells import shell  # noqa: E402


def _get_shell_pid() -> int:
    """Returns parent process pid."""
    proc = Process(os.getpid())

    try:
        return proc.parent().pid
    except TypeError:
        return proc.parent.pid


def _get_not_configured_usage_tracker_path() -> Path:
    """Returns path of special file where we store latest shell pid."""
    return Path(gettempdir()).joinpath(
        f"thefuck.last_not_configured_run_{getpass.getuser()}"
    )


def _record_first_run() -> None:
    """Records shell pid to tracker file."""
    info = {"pid": _get_shell_pid(), "time": time.time()}

    mode = "w"
    with _get_not_configured_usage_tracker_path().open(mode) as tracker:
        json.dump(info, tracker)


def _get_previous_command() -> str | None:
    history = shell.get_history()

    if history:
        return history[-1]
    return None


def _is_second_run() -> bool:
    """Returns `True` when we know that `fuck` called second time."""
    tracker_path = _get_not_configured_usage_tracker_path()
    if not tracker_path.exists():
        return False

    current_pid = _get_shell_pid()
    with tracker_path.open("r") as tracker:
        try:
            info = json.load(tracker)
        except ValueError:
            return False

    if not (isinstance(info, dict) and info.get("pid") == current_pid):
        return False

    return (
        _get_previous_command() == "fuck"
        or time.time() - info.get("time", 0) < const.CONFIGURATION_TIMEOUT
    )


def _is_already_configured(configuration_details) -> bool:
    """Returns `True` when alias already in shell config."""
    path = Path(configuration_details.path).expanduser()
    with path.open("r") as shell_config:
        return configuration_details.content in shell_config.read()


def _configure(configuration_details) -> None:
    """Adds alias to shell config."""
    path = Path(configuration_details.path).expanduser()
    with path.open("a") as shell_config:
        shell_config.write("\n")
        shell_config.write(configuration_details.content)
        shell_config.write("\n")


def main() -> None:
    """
    Shows useful information about how-to configure alias on a first run
    and configure automatically on a second.

    It'll be only visible when user type fuck and when alias isn't configured.

    """
    settings.init()
    configuration_details = shell.how_to_configure()
    if configuration_details and configuration_details.can_configure_automatically:
        if _is_already_configured(configuration_details):
            logs.already_configured(configuration_details)
            return
        if _is_second_run():
            _configure(configuration_details)
            logs.configured_successfully(configuration_details)
            return
        _record_first_run()

    logs.how_to_configure_alias(configuration_details)
