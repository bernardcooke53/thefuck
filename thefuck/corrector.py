from __future__ import annotations

import sys
from collections.abc import Generator, Iterable, Iterator
from pathlib import Path

from thefuck import logs
from thefuck.conf import settings
from thefuck.types import Command, CorrectedCommand, Rule


def get_loaded_rules(rules_paths: Iterable[Path]) -> Iterable[Rule]:
    """
    Yields all available rules.
    """
    for path in rules_paths:
        if path.name != "__init__.py":
            rule = Rule.from_path(path)
            if rule and rule.is_enabled:
                yield rule


def get_rules_import_paths() -> Generator[Path]:
    """
    Yields all rules import paths.
    """
    # Bundled rules:
    yield Path(__file__).parent.joinpath("rules")
    # Rules defined by user:
    yield settings.user_dir.joinpath("rules")
    # Packages with third-party rules:
    for path in sys.path:
        for contrib_module in Path(path).glob("thefuck_contrib_*"):
            contrib_rules = contrib_module.joinpath("rules")
            if contrib_rules.is_dir():
                yield contrib_rules


def get_rules() -> list[Rule]:
    """
    Returns all enabled rules.
    """
    paths = [
        rule_path
        for path in get_rules_import_paths()
        for rule_path in sorted(path.glob("*.py"))
    ]
    return sorted(get_loaded_rules(paths), key=lambda rule: rule.priority)


def organize_commands(
    corrected_commands: Iterator[CorrectedCommand],
) -> Generator[CorrectedCommand]:
    """
    Yields sorted commands without duplicates.
    """
    try:
        first_command = next(corrected_commands)
        yield first_command
    except StopIteration:
        return

    without_duplicates = {
        command
        for command in sorted(corrected_commands, key=lambda command: command.priority)
        if command != first_command
    }

    sorted_commands = sorted(
        without_duplicates, key=lambda corrected_command: corrected_command.priority
    )

    logs.debug(
        "Corrected commands: {}".format(
            ", ".join(f"{cmd}" for cmd in [first_command] + sorted_commands)
        )
    )

    yield from sorted_commands


def get_corrected_commands(command: Command) -> Iterator[CorrectedCommand]:
    """
    Returns generator with sorted and unique corrected commands.

    :type command: thefuck.types.Command
    :rtype: Iterable[thefuck.types.CorrectedCommand]

    """
    corrected_commands = (
        corrected
        for rule in get_rules()
        if rule.is_match(command)
        for corrected in rule.get_corrected_commands(command)
    )
    return organize_commands(corrected_commands)
