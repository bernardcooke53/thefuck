from __future__ import annotations

import msvcrt

import win_unicode_console

from .. import const


def init_output():
    import colorama

    win_unicode_console.enable()
    colorama.init()


def get_key():
    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):  # arrow or function key prefix?
        ch = msvcrt.getwch()  # second call returns the actual key code

    if ch in const.KEY_MAPPING:
        return const.KEY_MAPPING[ch]
    if ch == "H":
        return const.KEY_UP
    if ch == "P":
        return const.KEY_DOWN

    return ch


def open_command(arg):
    return "cmd /c start " + arg
