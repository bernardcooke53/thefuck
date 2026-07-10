from __future__ import annotations

import shutil

from thefuck.conf import settings
from thefuck.logs import warn
from thefuck.shells import shell


def _get_alias(known_args) -> str:
    alias = shell.app_alias(known_args.alias)

    if known_args.enable_experimental_instant_mode:
        if not shutil.which("script"):
            warn("Instant mode requires `script` app")
        else:
            return shell.instant_mode_alias(known_args.alias)

    return alias


def print_alias(known_args) -> str:
    settings.init(known_args)
    print(_get_alias(known_args))
