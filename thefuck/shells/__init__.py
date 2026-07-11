"""
Package with shell specific actions, each shell class should
implement `from_shell`, `to_shell`, `app_alias`, `put_to_history` and
`get_aliases` methods.
"""

from __future__ import annotations

import os

from psutil import Process

from thefuck.shells.bash import Bash
from thefuck.shells.fish import Fish
from thefuck.shells.generic import Generic
from thefuck.shells.powershell import Powershell
from thefuck.shells.tcsh import Tcsh
from thefuck.shells.zsh import Zsh

shells = {
    "bash": Bash,
    "fish": Fish,
    "zsh": Zsh,
    "csh": Tcsh,
    "tcsh": Tcsh,
    "powershell": Powershell,
    "pwsh": Powershell,
}


def _get_shell_from_env() -> Generic | None:
    name = os.environ.get("TF_SHELL")

    if name in shells:
        return shells[name]()
    return None


def _get_shell_from_proc() -> Generic:
    proc = Process(os.getpid())

    while proc is not None and proc.pid > 0:
        name = os.path.splitext(proc.name())[0]

        if name in shells:
            return shells[name]()
        proc = proc.parent()

    return Generic()


shell = _get_shell_from_env() or _get_shell_from_proc()
