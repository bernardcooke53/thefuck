from __future__ import annotations

import shutil
import sys
import termios
import tty

import colorama

from .. import const

init_output = colorama.init


def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def get_key():
    ch = getch()

    if ch in const.KEY_MAPPING:
        return const.KEY_MAPPING[ch]
    if ch == "\x1b":
        next_ch = getch()
        if next_ch == "[":
            last_ch = getch()

            if last_ch == "A":
                return const.KEY_UP
            if last_ch == "B":
                return const.KEY_DOWN

    return ch


def open_command(arg):
    if shutil.which("xdg-open"):
        return "xdg-open " + arg
    return "open " + arg
