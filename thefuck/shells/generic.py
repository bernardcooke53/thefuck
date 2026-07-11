from __future__ import annotations

from collections.abc import Generator
import os
import shlex
from pathlib import Path
from typing import NamedTuple

from thefuck.conf import settings
from thefuck.logs import warn
from thefuck.utils import memoize


class ShellConfiguration(NamedTuple):
    content: str
    path: str
    reload: str
    can_configure_automatically: bool


class Generic:
    friendly_name = "Generic Shell"

    def get_aliases(self) -> dict[str, str]:
        return {}

    def _expand_aliases(self, command_script: str) -> str:
        aliases = self.get_aliases()
        binary = command_script.split(" ")[0]
        if binary in aliases:
            return command_script.replace(binary, aliases[binary], 1)
        return command_script

    def from_shell(self, command_script: str) -> str:
        """Prepares command before running in app."""
        return self._expand_aliases(command_script)

    def to_shell(self, command_script: str) -> str:
        """Prepares command for running in shell."""
        return command_script

    def app_alias(self, alias_name: str) -> str:
        return (
            f"""alias {alias_name}='eval "$(TF_ALIAS={alias_name} PYTHONIOENCODING=utf-8 """
            """thefuck "$(fc -ln -1)")"'"""
        )

    def instant_mode_alias(self, alias_name: str) -> str:
        warn("Instant mode not supported by your shell")
        return self.app_alias(alias_name)

    def _get_history_file_name(self) -> str:
        return ""

    def _get_history_line(self, command_script: str) -> str:
        return ""

    @memoize
    def get_history(self) -> list[str]:
        return list(self._get_history_lines())

    def _get_history_lines(self) -> Generator[str]:
        """Returns list of history entries."""
        history_file_name = self._get_history_file_name()
        if os.path.isfile(history_file_name):
            with open(
                history_file_name, encoding="utf-8", errors="ignore"
            ) as history_file:
                lines = history_file.readlines()
                if settings.history_limit:
                    lines = lines[-settings.history_limit :]

                for line in lines:
                    prepared = self._script_from_history(line).strip()
                    if prepared:
                        yield prepared

    def and_(self, *commands: str) -> str:
        return " && ".join(commands)

    def or_(self, *commands: str) -> str:
        return " || ".join(commands)

    def how_to_configure(self) -> None:
        return

    def split_command(self, command: str) -> list[str]:
        """Split the command using shell-like syntax."""
        encoded = self.encode_utf8(command)

        try:
            splitted = [
                s.replace("??", "\\ ")
                for s in shlex.split(encoded.replace("\\ ", "??"))
            ]
        except ValueError:
            splitted = encoded.split(" ")

        return self.decode_utf8(splitted)

    def encode_utf8(self, command: str) -> str:
        return command

    def decode_utf8(self, command_parts: list[str]) -> list[str]:
        return command_parts

    def quote(self, s: str) -> str:
        """Return a shell-escaped version of the string s."""
        return shlex.quote(s)

    def _script_from_history(self, line: str) -> str:
        return line

    def put_to_history(self, command: str) -> None:
        """
        Adds fixed command to shell history.

        In most of shells we change history on shell-level, but not
        all shells support it (Fish).
        """

    def get_builtin_commands(self) -> list[str]:
        """Returns shells builtin commands."""
        return [
            "alias",
            "bg",
            "bind",
            "break",
            "builtin",
            "case",
            "cd",
            "command",
            "compgen",
            "complete",
            "continue",
            "declare",
            "dirs",
            "disown",
            "echo",
            "enable",
            "eval",
            "exec",
            "exit",
            "export",
            "fc",
            "fg",
            "getopts",
            "hash",
            "help",
            "history",
            "if",
            "jobs",
            "kill",
            "let",
            "local",
            "logout",
            "popd",
            "printf",
            "pushd",
            "pwd",
            "read",
            "readonly",
            "return",
            "set",
            "shift",
            "shopt",
            "source",
            "suspend",
            "test",
            "times",
            "trap",
            "type",
            "typeset",
            "ulimit",
            "umask",
            "unalias",
            "unset",
            "until",
            "wait",
            "while",
        ]

    def _get_version(self) -> str:
        """Returns the version of the current shell"""
        return ""

    def info(self) -> str:
        """Returns the name and version of the current shell"""
        try:
            version = self._get_version()
        except Exception as e:
            warn(f"Could not determine shell version: {e}")
            version = ""
        return f"{self.friendly_name} {version}".rstrip()

    def _create_shell_configuration(
        self, content: str, path: str, reload: str
    ) -> ShellConfiguration:
        return ShellConfiguration(
            content=content,
            path=path,
            reload=reload,
            can_configure_automatically=Path(path).expanduser().exists(),
        )
