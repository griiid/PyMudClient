import fcntl
import os
import sys

from pymudclient.shared_data import g_input
from pymudclient.utils.codec import enc
from pymudclient.utils.colors import color_convert

# ANSI Escape Code: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797


class UnblockTTY:

    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.flags_save = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        flags = self.flags_save & ~os.O_NONBLOCK
        fcntl.fcntl(self.fd, fcntl.F_SETFL, flags)

    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.flags_save)


def _unblock_print(*args, **kwargs):
    with UnblockTTY():
        print(*args, **kwargs)


def _set_end(kwargs):
    if 'end' not in kwargs:
        kwargs['end'] = '\r\n'


def color_print(text, *args, **kwargs):
    text = color_convert(text)
    _set_end(kwargs)
    _unblock_print(text, *args, **kwargs)


def replace_line_print(text, color=True, *args, **kwargs):
    if color:
        color_print(f'\x1B[2K\r{text}\x1B[m', *args, **kwargs)
    else:
        _unblock_print(f'\x1B[2K\r{text}\x1B[m', *args, **kwargs)


def move_cursor_to_index():
    if g_input['input_index'] <= 0:
        return

    cursor_pos = len(enc(g_input['input'][:g_input['input_index']]))
    # Move cursor to index
    sys.stdout.write(u'\u001B[' + str(cursor_pos) + 'C')
    sys.stdout.flush()
