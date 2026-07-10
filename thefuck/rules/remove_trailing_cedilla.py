from __future__ import annotations

CEDILLA = "ç"


def match(command):
    return command.script.endswith(CEDILLA)


def get_new_command(command):
    return command.script[:-1]
