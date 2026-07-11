from __future__ import annotations

import os
from subprocess import PIPE, Popen
from tempfile import gettempdir
from uuid import uuid4

from thefuck.shells.generic import Generic, ShellConfiguration
from thefuck.conf import settings
from thefuck.const import ARGUMENT_PLACEHOLDER, USER_COMMAND_MARK
from thefuck.utils import DEVNULL, memoize


class Bash(Generic):
    friendly_name = "Bash"

    def app_alias(self, alias_name: str) -> str:
        # It is VERY important to have the variables declared WITHIN the function
        return """
            function {name} () {{
                TF_PYTHONIOENCODING=$PYTHONIOENCODING;
                export TF_SHELL=bash;
                export TF_ALIAS={name};
                export TF_SHELL_ALIASES=$(alias);
                export TF_HISTORY=$(fc -ln -10);
                export PYTHONIOENCODING=utf-8;
                TF_CMD=$(
                    thefuck {argument_placeholder} "$@"
                ) && eval "$TF_CMD";
                unset TF_HISTORY;
                export PYTHONIOENCODING=$TF_PYTHONIOENCODING;
                {alter_history}
            }}
        """.format(
            name=alias_name,
            argument_placeholder=ARGUMENT_PLACEHOLDER,
            alter_history=("history -s $TF_CMD;" if settings.alter_history else ""),
        )

    def instant_mode_alias(self, alias_name: str) -> str:
        if os.environ.get("THEFUCK_INSTANT_MODE", "").lower() == "true":
            mark = USER_COMMAND_MARK + "\b" * len(USER_COMMAND_MARK)
            return f"""
                export PS1="{mark}$PS1";
                {self.app_alias(alias_name)}
            """
        log_path = os.path.join(gettempdir(), f"thefuck-script-log-{uuid4().hex}")
        return f"""
                export THEFUCK_INSTANT_MODE=True;
                export THEFUCK_OUTPUT_LOG={log_path};
                thefuck --shell-logger {log_path};
                rm {log_path};
                exit
            """

    def _parse_alias(self, alias: str) -> tuple[str, str]:
        name, value = alias.replace("alias ", "", 1).split("=", 1)
        if value[0] == value[-1] == '"' or value[0] == value[-1] == "'":
            value = value[1:-1]
        return name, value

    @memoize
    def get_aliases(self) -> dict[str, str]:
        raw_aliases = os.environ.get("TF_SHELL_ALIASES", "").split("\n")
        return dict(
            self._parse_alias(alias) for alias in raw_aliases if alias and "=" in alias
        )

    def _get_history_file_name(self) -> str:
        return os.environ.get("HISTFILE", os.path.expanduser("~/.bash_history"))

    def _get_history_line(self, command_script: str) -> str:
        return f"{command_script}\n"

    def how_to_configure(self) -> ShellConfiguration:
        if os.path.join(os.path.expanduser("~"), ".bashrc"):
            config = "~/.bashrc"
        elif os.path.join(os.path.expanduser("~"), ".bash_profile"):
            config = "~/.bash_profile"
        else:
            config = "bash config"

        return self._create_shell_configuration(
            content='eval "$(thefuck --alias)"',
            path=config,
            reload=f"source {config}",
        )

    def _get_version(self) -> str:
        """Returns the version of the current shell"""
        proc = Popen(["bash", "-c", "echo $BASH_VERSION"], stdout=PIPE, stderr=DEVNULL)
        return proc.stdout.read().decode("utf-8").strip()
