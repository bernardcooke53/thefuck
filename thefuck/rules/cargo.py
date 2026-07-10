from __future__ import annotations


def match(command):
    return command.script == "cargo"


def get_new_command(command):
    return "cargo build"
