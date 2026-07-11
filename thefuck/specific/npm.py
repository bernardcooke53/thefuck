from __future__ import annotations

import re
import shutil
from subprocess import PIPE, Popen
from typing import Generator

from thefuck.utils import eager, memoize

npm_available = bool(shutil.which("npm"))


@memoize
@eager
def get_scripts() -> Generator[str]:
    """Get custom npm scripts."""
    proc = Popen(["npm", "run-script"], stdout=PIPE)
    should_yield = False
    for line in proc.stdout.readlines():
        line = line.decode()
        if "available via `npm run-script`:" in line:
            should_yield = True
            continue

        if should_yield and re.match(r"^  [^ ]+", line):
            yield line.strip().split(" ")[0]
