from __future__ import annotations

import sys
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from traceback import format_exception
from types import TracebackType
from typing import TypeAlias

import colorama

from thefuck import const
from thefuck.conf import settings
from thefuck.shells.generic import ShellConfiguration
from thefuck.types import CorrectedCommand, Rule

_ExcInfo: TypeAlias = tuple[type[BaseException], Exception, TracebackType]


def color(color_: str) -> str:
    """Utility for ability to disabling colored output."""
    if settings.no_colors:
        return ""
    return color_


def warn(title: str) -> None:
    sys.stderr.write(
        f"{color(colorama.Back.RED + colorama.Fore.WHITE + colorama.Style.BRIGHT)}[WARN] {title}{color(colorama.Style.RESET_ALL)}\n"
    )


def exception(title: str, exc_info: _ExcInfo) -> None:
    sys.stderr.write(
        "{warn}[WARN] {title}:{reset}\n{trace}"
        "{warn}----------------------------{reset}\n\n".format(
            warn=color(colorama.Back.RED + colorama.Fore.WHITE + colorama.Style.BRIGHT),
            reset=color(colorama.Style.RESET_ALL),
            title=title,
            trace="".join(format_exception(*exc_info)),
        )
    )


def rule_failed(rule: Rule, exc_info: _ExcInfo) -> None:
    exception(f"Rule {rule.name}", exc_info)


def failed(msg: str) -> None:
    sys.stderr.write(
        f"{color(colorama.Fore.RED)}{msg}{color(colorama.Style.RESET_ALL)}\n"
    )


def show_corrected_command(corrected_command: CorrectedCommand) -> None:
    sys.stderr.write(
        "{prefix}{bold}{script}{reset}{side_effect}\n".format(
            prefix=const.USER_COMMAND_MARK,
            script=corrected_command.script,
            side_effect=" (+side effect)" if corrected_command.side_effect else "",
            bold=color(colorama.Style.BRIGHT),
            reset=color(colorama.Style.RESET_ALL),
        )
    )


def confirm_text(corrected_command: CorrectedCommand) -> None:
    sys.stderr.write(
        (
            "{prefix}{clear}{bold}{script}{reset}{side_effect} "
            "[{green}enter{reset}/{blue}↑{reset}/{blue}↓{reset}"
            "/{red}ctrl+c{reset}]"
        ).format(
            prefix=const.USER_COMMAND_MARK,
            script=corrected_command.script,
            side_effect=" (+side effect)" if corrected_command.side_effect else "",
            clear="\033[1K\r",
            bold=color(colorama.Style.BRIGHT),
            green=color(colorama.Fore.GREEN),
            red=color(colorama.Fore.RED),
            reset=color(colorama.Style.RESET_ALL),
            blue=color(colorama.Fore.BLUE),
        )
    )


def debug(msg: str) -> None:
    if settings.debug:
        sys.stderr.write(
            f"{color(colorama.Fore.BLUE)}{color(colorama.Style.BRIGHT)}DEBUG:{color(colorama.Style.RESET_ALL)} {msg}\n"
        )


@contextmanager
def debug_time(msg: str) -> Generator[None]:
    started = datetime.now()
    try:
        yield
    finally:
        debug(f"{msg} took: {datetime.now() - started}")


def how_to_configure_alias(configuration_details: ShellConfiguration) -> None:
    print(
        f"Seems like {color(colorama.Style.BRIGHT)}fuck{color(colorama.Style.RESET_ALL)} alias isn't configured!"
    )

    if configuration_details:
        print(
            "Please put {bold}{content}{reset} in your "
            "{bold}{path}{reset} and apply "
            "changes with {bold}{reload}{reset} or restart your shell.".format(
                bold=color(colorama.Style.BRIGHT),
                reset=color(colorama.Style.RESET_ALL),
                **configuration_details._asdict(),
            )
        )

        if configuration_details.can_configure_automatically:
            print(
                f"Or run {color(colorama.Style.BRIGHT)}fuck{color(colorama.Style.RESET_ALL)} a second time to configure"
                " it automatically."
            )

    print(
        "More details - https://github.com/bernardcooke53/thefuck#manual-installation"
    )


def already_configured(configuration_details: ShellConfiguration) -> None:
    print(
        f"Seems like {color(colorama.Style.BRIGHT)}fuck{color(colorama.Style.RESET_ALL)} alias already configured!\n"
        f"For applying changes run {color(colorama.Style.BRIGHT)}{configuration_details.reload}{color(colorama.Style.RESET_ALL)}"
        " or restart your shell."
    )


def configured_successfully(configuration_details: ShellConfiguration) -> None:
    print(
        f"{color(colorama.Style.BRIGHT)}fuck{color(colorama.Style.RESET_ALL)} alias configured successfully!\n"
        f"For applying changes run {color(colorama.Style.BRIGHT)}{configuration_details.reload}{color(colorama.Style.RESET_ALL)}"
        " or restart your shell."
    )


def version(thefuck_version: str, python_version: str, shell_info: str) -> None:
    sys.stderr.write(
        f"The Fuck {thefuck_version} using Python {python_version} and {shell_info}\n"
    )
