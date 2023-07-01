import os

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

    def __init__(self):
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
