from __future__ import annotations

import os
from subprocess import PIPE, Popen
from time import time

from thefuck.shells.generic import Generic, ShellConfiguration
from thefuck.utils import DEVNULL, memoize


class Tcsh(Generic):
    friendly_name = "Tcsh"

    def app_alias(self, alias_name: str) -> str:
        return (
            f"alias {alias_name} 'setenv TF_SHELL tcsh && setenv TF_ALIAS {alias_name} && "
            "set fucked_cmd=`history -h 2 | head -n 1` && "
            "eval `thefuck ${fucked_cmd}`'"
        )

    def _parse_alias(self, alias: str) -> tuple[str, str]:
        name, value = alias.split("\t", 1)
        return name, value

    @memoize
    def get_aliases(self) -> dict[str, str]:
        proc = Popen(["tcsh", "-ic", "alias"], stdout=PIPE, stderr=DEVNULL)
        return dict(
            self._parse_alias(alias)
            for alias in proc.stdout.read().decode("utf-8").split("\n")
            if alias and "\t" in alias
        )

    def _get_history_file_name(self) -> str:
        return os.environ.get("HISTFILE", os.path.expanduser("~/.history"))

    def _get_history_line(self, command_script: str) -> str:
        return f"#+{int(time())}\n{command_script}\n"

    def how_to_configure(self) -> ShellConfiguration:
        return self._create_shell_configuration(
            content="eval `thefuck --alias`", path="~/.tcshrc", reload="tcsh"
        )

    def _get_version(self) -> str:
        """Returns the version of the current shell"""
        proc = Popen(["tcsh", "--version"], stdout=PIPE, stderr=DEVNULL)
        return proc.stdout.read().decode("utf-8").split()[1]
