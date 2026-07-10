from __future__ import annotations

import shutil

nix_available = bool(shutil.which("nix"))
