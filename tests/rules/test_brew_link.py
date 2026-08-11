from __future__ import annotations

import pytest

from thefuck.rules.brew_link import get_new_command, match
from thefuck.types import Command


@pytest.fixture
def output() -> str:
    return (
        "Error: Could not symlink bin/gcp\n"
        "Target /usr/local/bin/gcp\n"
        "already exists. You may want to remove it:\n"
        "  rm '/usr/local/bin/gcp'\n"
        "\n"
        "To force the link and overwrite all conflicting files:\n"
        "  brew link --overwrite coreutils\n"
        "\n"
        "To list all files that would be deleted:\n"
        "  brew link --overwrite --dry-run coreutils\n"
    )


@pytest.fixture
def new_command(formula) -> str:
    return f"brew link --overwrite --dry-run {formula}"


@pytest.mark.parametrize("script", ["brew link coreutils", "brew ln coreutils"])
def test_match(output, script) -> None:
    assert match(Command(script, output))


@pytest.mark.parametrize("script", ["brew link coreutils"])
def test_not_match(script) -> None:
    assert not match(Command(script, ""))


@pytest.mark.parametrize("script, formula, ", [("brew link coreutils", "coreutils")])
def test_get_new_command(output, new_command, script, formula) -> None:
    assert get_new_command(Command(script, output)) == new_command
