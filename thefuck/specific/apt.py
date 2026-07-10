from __future__ import annotations

import shutil

apt_available = bool(shutil.which("apt-get"))
