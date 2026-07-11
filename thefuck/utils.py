from __future__ import annotations

import atexit
import dbm
import os
import pickle
import re
import shelve
import sys
from collections.abc import Callable, Iterable
from difflib import get_close_matches as difflib_get_close_matches
from functools import wraps
from pathlib import Path
from typing import Any, Generator, cast

# TODO: maybe this dep can be removed
from decorator import decorator

from thefuck.conf import settings
from thefuck.logs import exception, warn
from thefuck.types import Command
from thefuck.shells import shell
from importlib.metadata import version

# TODO: can we just use os.devnull?
DEVNULL = open(os.devnull, "w")


# TODO: can we just use functools.cache?
def memoize(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Caches previous calls to the function."""
    memo = {}

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not memoize.disabled:
            key = pickle.dumps((args, kwargs))
            if key not in memo:
                memo[key] = fn(*args, **kwargs)
            value = memo[key]
        else:
            # Memoize is disabled, call the function
            value = fn(*args, **kwargs)

        return value

    return wrapper


memoize.disabled = False


# TODO: can we just use the stdlib decorator machinery?
def default_settings(params: dict[str, str]) -> Callable[..., Any]:
    """
    Adds default values to settings if it not presented.

    Usage:

        @default_settings({'apt': '/usr/bin/apt'})
        def match(command):
            print(settings.apt)

    """

    def _default_settings(
        fn: Callable[..., dict[str, str]], command: Command
    ) -> dict[str, str]:
        for k, w in params.items():
            settings.setdefault(k, w)
        return fn(command)

    return decorator(_default_settings)


def get_closest(
    word: str,
    possibilities: Iterable[str],
    cutoff: float = 0.6,
    fallback_to_first: bool = True,
) -> str | None:
    """Returns closest match or just first from possibilities."""
    possibilities = list(possibilities)
    try:
        return difflib_get_close_matches(word, possibilities, 1, cutoff)[0]
    except IndexError:
        if fallback_to_first:
            return possibilities[0]


def get_close_matches(
    word: str, possibilities: list[str], n: int | None = None, cutoff: float = 0.6
) -> list[str]:
    """Overrides `difflib.get_close_match` to control argument `n`."""
    if n is None:
        n = cast(int, settings.num_close_matches)
    return difflib_get_close_matches(word, possibilities, n, cutoff)


def include_path_in_search(path: str) -> bool:
    return not any(path.startswith(x) for x in settings.excluded_search_path_prefixes)


@memoize
def get_all_executables() -> list[str]:
    def _safe(fn: Callable[..., Any], fallback: Any) -> Any:
        try:
            return fn()
        except OSError:
            return fallback

    tf_alias = get_alias()
    tf_entry_points = ["thefuck", "fuck"]

    bins = [
        exe.name
        for path in os.environ.get("PATH", "").split(os.pathsep)
        if include_path_in_search(path)
        for exe in _safe(lambda: list(Path(path).iterdir()), [])
        if not _safe(exe.is_dir, True) and exe.name not in tf_entry_points
    ]
    aliases = [alias for alias in shell.get_aliases() if alias != tf_alias]

    return bins + aliases


def replace_argument(script: str, from_: str, to: str) -> str:
    """Replaces command line argument."""
    replaced_in_the_end = re.sub(f" {re.escape(from_)}$", f" {to}", script, count=1)
    if replaced_in_the_end != script:
        return replaced_in_the_end
    return script.replace(f" {from_} ", f" {to} ", 1)


@decorator
def eager(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> list[Any]:
    return list(fn(*args, **kwargs))


@eager
def get_all_matched_commands(
    stderr: str, separator: str = "Did you mean"
) -> Generator[str]:
    if not isinstance(separator, list):
        separator = [separator]
    should_yield = False
    for line in stderr.split("\n"):
        for sep in separator:
            if sep in line:
                should_yield = True
                break
        else:
            if should_yield and line:
                yield line.strip()


def replace_command(command: Command, broken: str, matched: list[str]) -> list[str]:
    """Helper for *_no_command rules."""
    new_cmds = get_close_matches(broken, matched, cutoff=0.1)
    return [
        replace_argument(command.script, broken, new_cmd.strip())
        for new_cmd in new_cmds
    ]


@memoize
def is_app(command: Command, *app_names: str, **kwargs: Any) -> bool:
    """Returns `True` if command is call to one of passed app names."""
    at_least = kwargs.pop("at_least", 0)
    if kwargs:
        raise TypeError(f"got an unexpected keyword argument '{kwargs.keys()}'")

    if len(command.script_parts) > at_least:
        return os.path.basename(command.script_parts[0]) in app_names

    return False


def for_app(*app_names: str, **kwargs: Any) -> Any:
    """Specifies that matching script is for one of app names."""

    def _for_app(fn: Callable[..., Any], command: Command) -> Any:
        if is_app(command, *app_names, **kwargs):
            return fn(command)
        return False

    return decorator(_for_app)


class Cache:
    """Lazy read cache and save changes at exit."""

    def __init__(self) -> None:
        self._db = None

    def _init_db(self) -> None:
        try:
            self._setup_db()
        except Exception:
            exception("Unable to init cache", sys.exc_info())
            self._db = {}

    def _setup_db(self) -> None:
        cache_dir = self._get_cache_dir()
        cache_path = Path(cache_dir).joinpath("thefuck").as_posix()

        try:
            self._db = shelve.open(cache_path)
        except dbm.error + (ImportError,):
            # Caused when switching between Python versions
            warn("Removing possibly out-dated cache")
            os.remove(cache_path)
            self._db = shelve.open(cache_path)

        atexit.register(self._db.close)

    def _get_cache_dir(self) -> str:
        default_xdg_cache_dir = os.path.expanduser("~/.cache")
        cache_dir = os.getenv("XDG_CACHE_HOME", default_xdg_cache_dir)

        # Ensure the cache_path exists, Python 2 does not have the exist_ok
        # parameter
        try:
            os.makedirs(cache_dir)
        except OSError:
            if not os.path.isdir(cache_dir):
                raise

        return cache_dir

    def _get_mtime(self, path: str) -> str:
        try:
            return str(os.path.getmtime(path))
        except OSError:
            return "0"

    def _get_key(
        self, fn: Callable[..., Any], depends_on: Any, args: Any, kwargs: Any
    ) -> str:
        parts = (fn.__module__, repr(fn).split("at")[0], depends_on, args, kwargs)
        return str(pickle.dumps(parts))

    def get_value(
        self, fn: Callable[..., Any], depends_on: Any, args: Any, kwargs: Any
    ) -> Any:
        if self._db is None:
            self._init_db()

        depends_on = [
            Path(name).expanduser().absolute().as_posix() for name in depends_on
        ]
        key = self._get_key(fn, depends_on, args, kwargs)
        etag = ".".join(self._get_mtime(path) for path in depends_on)

        if self._db.get(key, {}).get("etag") == etag:
            return self._db[key]["value"]
        value = fn(*args, **kwargs)
        self._db[key] = {"etag": etag, "value": value}
        return value


_cache = Cache()


def cache(*depends_on: Any) -> Any:
    """
    Caches function result in temporary file.

    Cache will be expired when modification date of files from `depends_on`
    will be changed.

    Only functions should be wrapped in `cache`, not methods.

    """

    def cache_decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @memoize
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if cache.disabled:
                return fn(*args, **kwargs)
            return _cache.get_value(fn, depends_on, args, kwargs)

        return wrapper

    return cache_decorator


cache.disabled = False


def get_installation_version() -> str:
    return version("thefuck")


def get_alias() -> str:
    return os.environ.get("TF_ALIAS", "fuck")


@memoize
def get_valid_history_without_current(command: Command) -> list[str]:
    def _not_corrected(history, tf_alias):
        """Returns all lines from history except that comes before `fuck`."""
        previous = None
        for line in history:
            if previous is not None and line != tf_alias:
                yield previous
            previous = line
        if history:
            yield history[-1]

    history = shell.get_history()
    tf_alias = get_alias()
    executables = set(get_all_executables()).union(shell.get_builtin_commands())

    return [
        line
        for line in _not_corrected(history, tf_alias)
        if not line.startswith(tf_alias)
        and line != command.script
        and line.split(" ")[0] in executables
    ]


def format_raw_script(raw_script: list[str]) -> str:
    """
    Creates single script from a list of script parts.

    :type raw_script: [basestring]
    :rtype: basestring

    """
    script = " ".join(raw_script)
    return script.lstrip()
