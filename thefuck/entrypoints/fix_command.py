from __future__ import annotations

import os
import sys
from difflib import SequenceMatcher
from pprint import pformat

from thefuck import const, logs, types
from thefuck.conf import settings
from thefuck.corrector import get_corrected_commands
from thefuck.exceptions import EmptyCommand
from thefuck.ui import select_command
from thefuck.utils import get_alias, get_all_executables


def _get_raw_command(known_args) -> list[str]:
    if known_args.force_command:
        return [known_args.force_command]
    if not os.environ.get("TF_HISTORY"):
        return known_args.command
    history = os.environ["TF_HISTORY"].split("\n")[::-1]
    alias = get_alias()
    executables = get_all_executables()
    for command in history:
        diff = SequenceMatcher(a=alias, b=command).ratio()
        if diff < const.DIFF_WITH_ALIAS or command in executables:
            return [command]
    return []


def fix_command(known_args) -> None:
    """Fixes previous command. Used when `thefuck` called without arguments."""
    settings.init(known_args)
    with logs.debug_time("Total"):
        logs.debug(f"Run with settings: {pformat(settings)}")
        raw_command = _get_raw_command(known_args)

        try:
            command = types.Command.from_raw_script(raw_command)
        except EmptyCommand:
            logs.debug("Empty command, nothing to do")
            return

        corrected_commands = get_corrected_commands(command)
        selected_command = select_command(corrected_commands)

        if selected_command:
            selected_command.run(command)
        else:
            sys.exit(1)
