import sys
import time
from dataclasses import dataclass
from typing import Callable

from .display import show_input
from .kbhit import KBHit
from .shared_data import (
    g_input,
    g_is_reconnect,
    g_is_running,
)
from .utils.print import color_print
from .utils.telnet import send_to_host

kb = KBHit()

alias_list = None


def _getch():
    if not kb.kbhit():
        return None
    return kb.getch()


def _input_visible(char, char_ord):
    '''ASCII 可視字元 或 中文字'''

    if char_ord < 0x20 or 0x7E < char_ord < 0x4E00 or 0x9FA5 < char_ord:
        return

    if g_input['last_send'] != '':
        g_input['last_send'] = ''

    g_input['input'] = (
        g_input['input'][:g_input['input_index']] + char + g_input['input'][g_input['input_index']:]
    )
    g_input['input_index'] += 1


def _input_ctrl_c(_, char_ord):
    if char_ord != 0x03:
        return False

    g_input['is_running'] = False
    color_print('\r\n$HIY$中斷程式$NOR$')
    return True


def _input_0x1B(_, char_ord):
    if char_ord != 0x1B:
        # Not Special Command
        return

    next1, next2 = ord(sys.stdin.read(1)), ord(sys.stdin.read(1))
    if next1 != 91:
        return

    if next2 == 51:
        next3 = ord(sys.stdin.read(1))
        if next3 == 126:
            # Delete
            if g_input['last_send'] != '':
                g_input['last_send'] = ''
            else:
                g_input['input'] = (
                    g_input['input'][:g_input['input_index']] +
                    g_input['input'][g_input['input_index'] + 1:]
                )
    elif next2 == 68:
        # Left
        if g_input['last_send'] != '':
            g_input['input'] = g_input['last_send']
            g_input['input_index'] = len(g_input['last_send']) - 1
            g_input['last_send'] = ''
        else:
            g_input['input_index'] = max(0, g_input['input_index'] - 1)
    elif next2 == 67:
        # Right
        if g_input['last_send'] != '':
            g_input['input'] = g_input['last_send']
            g_input['input_index'] = len(g_input['last_send'])
            g_input['last_send'] = ''
        else:
            g_input['input_index'] = min(len(g_input['input']), g_input['input_index'] + 1)
    elif next2 == 70:
        # End
        if g_input['last_send'] != '':
            g_input['input'] = g_input['last_send']
            g_input['input_index'] = len(g_input['last_send'])
            g_input['last_send'] = ''
        else:
            g_input['input_index'] = len(g_input['input'])
    elif next2 == 72:
        # Home
        if g_input['last_send'] != '':
            g_input['input'] = g_input['last_send']
            g_input['input_index'] = 0
            g_input['last_send'] = ''
        else:
            g_input['input_index'] = 0


def _input_backspace(_, char_ord):
    if char_ord != 0x7F:
        # Not Backspace
        return

    if g_input['last_send'] != '':
        g_input['last_send'] = ''
    elif g_input['input_index'] > 0:
        g_input['input'] = (
            g_input['input'][:g_input['input_index'] - 1] + g_input['input'][g_input['input_index']:]
        )
        g_input['input_index'] -= 1


def _alias_pattern_process(start_text, pattern, text):
    text = text.replace(f'{start_text}', '', 1)
    split_text = text.split()
    params = {}

    # %0
    if '%0' in pattern:
        pattern = pattern.replace('%0', '{%0}')
        params['%0'] = text

    # 正數 %1 ~ %n
    i = 1
    while True:
        search = f'%{i}'
        if search not in pattern:
            break

        params[search] = split_text[i - 1]
        pattern = pattern.replace(search, f'{{{search}}}')
        i += 1

    # 負數 %-1 %-n
    i = 1
    while True:
        search = f'%-{i}'
        if search not in pattern:
            break

        params[search] = ' '.join(split_text[i:])
        pattern = pattern.replace(search, f'{{{search}}}')
        i += 1

    return pattern.format(**params)


def _alias_function(text):
    for alias in alias_list:
        if not text.startswith(alias.start_text):
            continue

        if alias.pattern:
            return _alias_pattern_process(alias.start_text, alias.pattern, text)
        if alias.func:
            return alias.func(text)

    return text


def _input_enter(_, char_ord):
    if char_ord in {0x0A, 0x0D}:    # Enter
        if g_input['last_send'] != '':
            g_input['input'] = g_input['last_send']
        else:
            g_input['last_send'] = g_input['input']

        text = g_input['input']
        text = _alias_function(text)
        if text:
            send_to_host(text)

        g_input['input'] = ''
        g_input['input_index'] = 0


@dataclass
class _Timer:

    seconds: int
    last_time: int
    data: str = None
    func: Callable = None


class TimerProcessor:

    def __init__(self, timer_list):
        last_time = time.time()
        self.timer_list = [_Timer(timer.seconds, last_time, timer.data, timer.func) for timer in timer_list]

    def process(self):
        for timer in self.timer_list:
            if time.time() - timer.last_time >= timer.seconds:
                timer.last_time = time.time()

                if timer.data:
                    send_to_host(timer.data)
                elif timer.func:
                    text = timer.func()
                    if text:
                        send_to_host(text)


INPUT_FUNCTION_LIST = [
    _input_visible,
    _input_0x1B,
    _input_backspace,
    _input_enter,
]


def thread_job_input_cmd(alias_list_, timer_list):
    global alias_list
    alias_list = alias_list_
    timer_processor = TimerProcessor(timer_list)

    while g_is_running.get() and not g_is_reconnect.get():
        char = _getch()
        if char is None:
            timer_processor.process()
            time.sleep(0.01)
            continue

        char_ord = ord(char)

        for func in INPUT_FUNCTION_LIST:
            if func(char, char_ord):
                return

        show_input()
