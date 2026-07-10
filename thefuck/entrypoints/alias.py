from __future__ import annotations

import shutil

from ..conf import settings
from ..logs import warn
from ..shells import shell


def _get_alias(known_args):
    alias = shell.app_alias(known_args.alias)

    if known_args.enable_experimental_instant_mode:
        if not shutil.which("script"):
            warn("Instant mode requires `script` app")
        else:
            return shell.instant_mode_alias(known_args.alias)

    return alias


def print_alias(known_args):
    settings.init(known_args)
    print(_get_alias(known_args))
