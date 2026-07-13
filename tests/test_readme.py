from __future__ import annotations

from pathlib import Path


def test_readme(source_root: Path) -> None:
    with source_root.joinpath("README.md").open() as f:
        readme = f.read()

        bundled = source_root.joinpath("thefuck").joinpath("rules").glob("*.py")

        for rule in bundled:
            if rule.stem != "__init__":
                assert rule.stem in readme, f'Missing rule "{rule.stem}" in README.md'
