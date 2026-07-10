from __future__ import annotations

import shutil
import subprocess

from ..utils import memoize

brew_available = bool(shutil.which("brew"))


@memoize
def get_brew_path_prefix():
    """To get brew path"""
    try:
        return subprocess.check_output(["brew", "--prefix"], text=True).strip()
    except Exception:
        return None
