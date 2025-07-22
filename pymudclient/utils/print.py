import fcntl
import os
import sys

from pymudclient import (
    configs,
    shared_data,
)
from pymudclient.utils.codec import encode
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
    for key, value in configs.VARIABLE_MAP.items():
        text = text.replace(f'${{{key}}}', value)

    new_args = []
    for arg in args:
        for key, value in configs.VARIABLE_MAP.items():
            arg = arg.replace(f'${{{key}}}', value)
        new_args.append(arg)

    text = color_convert(text)
    _set_end(kwargs)
    _unblock_print(text, *new_args, **kwargs)


def replace_line_print(text, color=True, *args, **kwargs):
    if color:
        color_print(f'\x1B[2K\r{text}\x1B[m', *args, **kwargs)
    else:
        _unblock_print(f'\x1B[2K\r{text}\x1B[m', *args, **kwargs)


def move_cursor_to_index():
    with shared_data.CURRENT_INPUT.locked():
        current_input_index = shared_data.CURRENT_INPUT['input_index']
        if current_input_index <= 0:
            return

        cursor_pos = len(encode(shared_data.CURRENT_INPUT['input'][:current_input_index]))
        # Move cursor to index
        sys.stdout.write(u'\u001B[' + str(cursor_pos) + 'C')
        sys.stdout.flush()
