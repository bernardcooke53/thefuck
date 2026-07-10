from __future__ import annotations

import shutil

yum_available = bool(shutil.which("yum"))
