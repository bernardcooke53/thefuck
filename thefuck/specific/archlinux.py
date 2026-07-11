"""This file provide some utility functions for Arch Linux specific rules."""

from __future__ import annotations

import shutil
import subprocess

from thefuck import utils


@utils.memoize
def get_pkgfile(command: str) -> list[str]:
    """
    Gets the packages that provide the given command using `pkgfile`.

    If the command is of the form `sudo foo`, searches for the `foo` command
    instead.
    """
    try:
        command = command.strip()

        command = command.removeprefix("sudo ")

        command = command.split(" ")[0]

        packages = subprocess.check_output(
            ["pkgfile", "-b", "-v", command],
            text=True,
            stderr=utils.DEVNULL,
        ).splitlines()

        return [package.split()[0] for package in packages]
    except subprocess.CalledProcessError as err:
        if err.returncode == 1 and err.output == "":
            return []
        raise err


def archlinux_env() -> tuple[str | bool | None, str | None]:
    if shutil.which("yay"):
        pacman = "yay"
    elif shutil.which("pikaur"):
        pacman = "pikaur"
    elif shutil.which("yaourt"):
        pacman = "yaourt"
    elif shutil.which("pacman"):
        pacman = "sudo pacman"
    else:
        return False, None

    enabled_by_default = shutil.which("pkgfile")

    return enabled_by_default, pacman
