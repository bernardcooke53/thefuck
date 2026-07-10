# Fixes careless " and ' usage
#
# Example:
# > git commit -m 'My Message"
from __future__ import annotations


def match(command):
    return "'" in command.script and '"' in command.script


def get_new_command(command):
    return command.script.replace("'", '"')
