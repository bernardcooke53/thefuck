from __future__ import annotations

import importlib.util
import os
import sys
from argparse import Namespace
from collections.abc import Generator
from pathlib import Path
from types import ModuleType
from typing import Any, TypeVar
from warnings import warn

from thefuck import const
from thefuck.logs import exception


def load_source(name: str, pathname: str, _file: None = None) -> ModuleType:
    module_spec = importlib.util.spec_from_file_location(name, pathname)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


_VT = TypeVar("_VT")


class Settings(dict[str, _VT]):
    def __getattr__(self, item: str) -> _VT | None:
        return self.get(item)

    def __setattr__(self, key: str, value: _VT) -> None:
        self[key] = value

    def init(self, args: Any | None = None) -> None:
        """Fills `settings` with values from `settings.py` and env."""
        self._setup_user_dir()
        self._init_settings_file()

        try:
            self.update(self._settings_from_file())
        except Exception:
            exception("Can't load settings from file", sys.exc_info())

        try:
            self.update(self._settings_from_env())
        except Exception:
            exception("Can't load settings from env", sys.exc_info())

        self.update(self._settings_from_args(args))

    def _init_settings_file(self) -> None:
        settings_path = self.user_dir.joinpath("settings.py")
        if not settings_path.is_file():
            with settings_path.open(mode="w") as settings_file:
                settings_file.write(const.SETTINGS_HEADER)
                for setting in const.DEFAULT_SETTINGS.items():
                    settings_file.write("# {} = {}\n".format(*setting))

    def _get_user_dir_path(self) -> Path:
        """Returns Path object representing the user config resource"""
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        user_dir = Path(xdg_config_home, "thefuck").expanduser()
        legacy_user_dir = Path("~", ".thefuck").expanduser()

        # For backward compatibility use legacy '~/.thefuck' if it exists:
        if legacy_user_dir.is_dir():
            warn(
                f"Config path {legacy_user_dir} is deprecated. Please move to {user_dir}",
                stacklevel=2,
            )
            return legacy_user_dir
        return user_dir

    def _setup_user_dir(self) -> None:
        """Returns user config dir, create it when it doesn't exist."""
        user_dir = self._get_user_dir_path()

        rules_dir = user_dir.joinpath("rules")
        if not rules_dir.is_dir():
            rules_dir.mkdir(parents=True)
        self.user_dir = user_dir

    def _settings_from_file(self) -> dict[str, Any]:
        """Loads settings from file."""
        settings = load_source("settings", str(self.user_dir.joinpath("settings.py")))
        return {
            key: getattr(settings, key)
            for key in const.DEFAULT_SETTINGS
            if hasattr(settings, key)
        }

    def _rules_from_env(self, val: str) -> list[Any]:
        """Transforms rules list from env-string to python."""
        split = val.split(":")
        if "DEFAULT_RULES" in split:
            split = const.DEFAULT_RULES + [
                rule for rule in split if rule != "DEFAULT_RULES"
            ]
        return split

    def _priority_from_env(self, val: str) -> Generator[tuple[str, int]]:
        """Gets priority pairs from env."""
        for part in val.split(":"):
            try:
                rule, priority = part.split("=")
                yield rule, int(priority)
            except ValueError:
                continue

    def _val_from_env(self, env: str, attr: str) -> Any:
        """Transforms env-strings to python."""
        val = os.environ[env]
        if attr in ("rules", "exclude_rules"):
            return self._rules_from_env(val)
        if attr == "priority":
            return dict(self._priority_from_env(val))
        if attr in (
            "wait_command",
            "history_limit",
            "wait_slow_command",
            "num_close_matches",
        ):
            return int(val)
        if attr in (
            "require_confirmation",
            "no_colors",
            "debug",
            "alter_history",
            "instant_mode",
        ):
            return val.lower() == "true"
        if attr in ("slow_commands", "excluded_search_path_prefixes"):
            return val.split(":")
        return val

    def _settings_from_env(self) -> dict[str, Any]:
        """Loads settings from env."""
        return {
            attr: self._val_from_env(env, attr)
            for env, attr in const.ENV_TO_ATTR.items()
            if env in os.environ
        }

    def _settings_from_args(self, args: Namespace) -> dict[str, Any]:
        """Loads settings from args."""
        if not args:
            return {}

        from_args = {}
        if args.yes:
            from_args["require_confirmation"] = not args.yes
        if args.debug:
            from_args["debug"] = args.debug
        if args.repeat:
            from_args["repeat"] = args.repeat
        return from_args


settings = Settings(const.DEFAULT_SETTINGS)
