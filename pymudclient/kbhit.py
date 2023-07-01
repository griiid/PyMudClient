import os
from enum import Enum
from functools import wraps

# Windows
if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import atexit
    import sys
    import termios
    import tty


class KBHit:

    Key = Enum(
        'Key',
        [
            'CTRL_C',
            'ESC',
            'UP',
            'DOWN',
            'LEFT',
            'RIGHT',
            'DELETE',
        ],
    )

    def __init__(self):
        self._last_ch = None
        self._last_ch_ord = None

        if os.name != 'nt':
            self._posix_setup()

    def _posix_setup(self):
        self.fd = sys.stdin.fileno()

        # Get origin tty control I/O attributes
        self.attr_origin = termios.tcgetattr(self.fd)

        # Support normal-terminal reset at exit
        atexit.register(self.set_normal_term)

        # Use raw terminal mode
        tty.setraw(self.fd, termios.TCSANOW)

        # Update tty control I/O attributes
        attr_new = termios.tcgetattr(self.fd)
        # The OPOST flag is responsible for enabling output processing,
        # including the transformation of \r to \r\n.
        attr_new[1] |= termios.OPOST
        # Don't echo input
        attr_new[3] &= ~termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSANOW, attr_new)

    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        if os.name == 'nt':
            pass
        else:
            termios.tcsetattr(self.fd, termios.TCSANOW, self.attr_origin)

    def _save_last_ch(func):

        @wraps(func)
        def wrapper(self, *args, **kargs):
            self._last_ch = func(self, *args, **kargs)
            self._last_ch_ord = ord(self._last_ch) if self._last_ch else None
            return self._last_ch

        return wrapper

    @_save_last_ch
    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''

        if os.name == 'nt':
            if not msvcrt.kbhit():
                return None
            return msvcrt.getch().decode('utf-8')
        else:
            try:
                return sys.stdin.read(1)
            except BlockingIOError:
                return None
            except Exception:
                return None

    # TODO: Implement
    def detect_special_key(self):
        if self._last_ch_ord == 0x03:
            return self.Key.CTRL_C


# Test
if __name__ == "__main__":

    kb = KBHit()

    print('Hit any key, or ctrl-c to exit')

    while True:
        ch = kb.getch()
        print(repr(ch))

        if ord(ch) == 0x03:
            # ctr-c
            break
