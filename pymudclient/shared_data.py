from enum import Enum

from pymudclient.utils.telnet import TelnetClient
from pymudclient.utils.thread_safe import ThreadSafe


class Status(Enum):

    START = 0
    RUNNING = 1
    RECONNECT = 2
    QUIT = 3


CONNECT_STATUS = ThreadSafe[Status](Status.QUIT)
CURRENT_INPUT = ThreadSafe[dict[
    str,
    str | int,
]]({
    'input': '',
    'last_send': '',
    'input_index': 0,
    'current_input_index': 0,
})
TN = ThreadSafe[TelnetClient](None)
