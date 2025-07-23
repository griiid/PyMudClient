import fcntl
import os
import select
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
            'CTRL_H',
            'CTRL_W',
            'ESC',
            'HOME',
            'END',
            'UP',
            'DOWN',
            'LEFT',
            'RIGHT',
            'BACKSPACE',
            'DELETE',
            'ENTER',
        ],
    )

    def __init__(self):
        self._last_char = None
        self._last_char_ord = None

        if os.name != 'nt':
            self._posix_setup()

    def _posix_setup(self):
        self.buffer = ''

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

        # Get the file access mode and the file status flags of
        # file control (fcntl)
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        # Set the file status flags to O_NONBLOCK
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)

    def set_normal_term(self):
        ''' Resets to normal terminal.  On Windows this is a no-op.
        '''

        if os.name == 'nt':
            pass
        else:
            termios.tcsetattr(self.fd, termios.TCSANOW, self.attr_origin)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

    def _save_last_char(func):

        @wraps(func)
        def wrapper(self, *args, **kargs):
            self._last_char = func(self, *args, **kargs)
            self._last_char_ord = ord(self._last_char) if self._last_char else None
            return self._last_char

        return wrapper

    @_save_last_char
    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''

        if os.name == 'nt':
            if not msvcrt.kbhit():
                return None
            return msvcrt.getch().decode('utf-8')
        else:
            # 如果 buffer 還有值，就從裡面取出一個字元回傳
            if self.buffer:
                char, self.buffer = self.buffer[0], self.buffer[1:]
                return char

            # 使用 select 來實現 0.01 秒超時
            ready, _, _ = select.select([sys.stdin], [], [], 0.01)
            if not ready:
                return None

            try:
                # 把 stdin 所有的值都讀進來先放到 buffer
                self.buffer = sys.stdin.read()
                if not self.buffer:
                    return None

                # 取出 buffer 的第一個字元回傳，剩下的繼續放在 buffer 裡面
                char, self.buffer = self.buffer[0], self.buffer[1:]
                return char
            except BlockingIOError:
                return None
            except Exception:
                return None

    def detect_special_key(self):
        if self._last_char_ord == 0x03:
            return self.Key.CTRL_C
        if self._last_char_ord == 0x7F:
            return self.Key.BACKSPACE
        if self._last_char_ord in {0x0A, 0x0D}:
            return self.Key.ENTER
        if self._last_char_ord == 0x08:
            return self.Key.CTRL_H
        if self._last_char_ord == 0x17:
            return self.Key.CTRL_W
        if self._last_char_ord == 0x1B:
            return self._process_0x1B()

        return None

    def _process_0x1B(self):
        next1, next2, next3 = self.getch(), self.getch(), self.getch()
        next1_ord = ord(next1) if next1 else None
        next2_ord = ord(next2) if next2 else None
        next3_ord = ord(next3) if next3 else None

        if next1_ord == None:
            return self.Key.ESC
        if next1_ord == 0x5B:
            return self._process_0x1B_0x5B(next2_ord, next3_ord)

        return None

    def _process_0x1B_0x5B(self, next2_ord, next3_ord):
        if next2_ord == 0x33:
            if next3_ord == 0x7E:
                return self.Key.DELETE
        elif next2_ord == 0x43:
            return self.Key.RIGHT
        elif next2_ord == 0x44:
            return self.Key.LEFT
        elif next2_ord == 0x46:
            return self.Key.END
        elif next2_ord == 0x48:
            return self.Key.HOME

        return None


# Test
if __name__ == '__main__':

    import time

    kb = KBHit()

    print('Hit any key, or ctrl-c to exit')

    while True:
        ch = kb.getch()
        if ch is None:
            time.sleep(0.01)
            continue

        print(repr(ch))
        if ord(ch) == 0x03:
            # ctr-c
            break
