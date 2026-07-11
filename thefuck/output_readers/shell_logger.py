from __future__ import annotations

import json
import os
import socket
from shutil import get_terminal_size

import pyte

from thefuck import const, logs


def _get_socket_path() -> str | None:
    return os.environ.get(const.SHELL_LOGGER_SOCKET_ENV)


def is_available() -> bool:
    """
    Returns `True` if shell logger socket available.
    """
    path = _get_socket_path()
    if not path:
        return False

    return os.path.exists(path)


def _get_last_n(n: int) -> list[str]:
    with socket.socket(socket.AF_UNIX) as client:
        # TODO: optional but None is not allowed
        client.connect(_get_socket_path())
        request = (
            json.dumps(
                {
                    "type": "list",
                    "count": n,
                }
            )
            + "\n"
        )
        client.sendall(request.encode("utf-8"))
        response = client.makefile().readline()
        return json.loads(response)["commands"]


def _get_output_lines(output: str) -> list[str]:
    lines = output.split("\n")
    screen = pyte.Screen(get_terminal_size().columns, len(lines))
    stream = pyte.Stream(screen)
    stream.feed("\n".join(lines))
    return screen.display


def get_output(script: str) -> str | None:
    """Gets command output from shell logger."""
    with logs.debug_time("Read output from external shell logger"):
        commands = _get_last_n(const.SHELL_LOGGER_LIMIT)
        for command in commands:
            if command["command"] == script:
                lines = _get_output_lines(command["output"])
                output = "\n".join(lines).strip()
                return output
            logs.warn("Output isn't available in shell logger")
            return None
