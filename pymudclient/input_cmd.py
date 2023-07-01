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

alias_list = None


def _input_visible(key, key_ord, is_special_key):
    # speical key，不在這邊處理
    if is_special_key:
        return

    # 不是ASCII 可視字元 或 中文字
    if key_ord < 0x20 or 0x7E < key_ord < 0x4E00 or 0x9FA5 < key_ord:
        return

    if g_input['last_send'] != '':
        g_input['last_send'] = ''

    g_input['input'] = (
        g_input['input'][:g_input['input_index']] + key + g_input['input'][g_input['input_index']:]
    )
    g_input['input_index'] += 1


# TODO: Implement
def _input_speicial_keys(key, key_ord, is_special_key):
    # 不是 speical key，不在這邊處理
    if not is_special_key:
        return

    if key == KBHit.Key.CTRL_C:
        _process_ctrl_c()
    elif key == KBHit.Key.BACKSPACE:
        _process_backspace()
    elif key == KBHit.Key.ENTER:
        _process_enter()
    elif key == KBHit.Key.DELETE:
        _process_delete()
    elif key == KBHit.Key.RIGHT:
        _process_right()
    elif key == KBHit.Key.LEFT:
        _process_left()
    elif key == KBHit.Key.HOME:
        _process_home()
    elif key == KBHit.Key.END:
        _process_end()


def _process_ctrl_c():
    g_is_running.set(False),
    color_print('\r\n$HIY$中斷程式$NOR$')
    return True


def _process_backspace():
    if g_input['last_send'] != '':
        g_input['last_send'] = ''
    elif g_input['input_index'] > 0:
        g_input['input'] = (
            g_input['input'][:g_input['input_index'] - 1] + g_input['input'][g_input['input_index']:]
        )
        g_input['input_index'] -= 1


def _process_enter():
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


def _process_delete():
    if g_input['last_send'] != '':
        g_input['last_send'] = ''
    else:
        g_input['input'] = (
            g_input['input'][:g_input['input_index']] +
            g_input['input'][g_input['input_index'] + 1:]
        )


def _process_right():
    if g_input['last_send'] != '':
        g_input['input'] = g_input['last_send']
        g_input['input_index'] = len(g_input['last_send'])
        g_input['last_send'] = ''
    else:
        g_input['input_index'] = min(len(g_input['input']), g_input['input_index'] + 1)


def _process_left():
    if g_input['last_send'] != '':
        g_input['input'] = g_input['last_send']
        g_input['input_index'] = len(g_input['last_send']) - 1
        g_input['last_send'] = ''
    else:
        g_input['input_index'] = max(0, g_input['input_index'] - 1)


def _process_home():
    if g_input['last_send'] != '':
        g_input['input'] = g_input['last_send']
        g_input['input_index'] = 0
        g_input['last_send'] = ''
    else:
        g_input['input_index'] = 0


def _process_end():
    if g_input['last_send'] != '':
        g_input['input'] = g_input['last_send']
        g_input['input_index'] = len(g_input['last_send'])
        g_input['last_send'] = ''
    else:
        g_input['input_index'] = len(g_input['input'])


def _alias_pattern_process(start_text, pattern, text):
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
        if text == alias.start_text:
            text = ''
        elif text.startswith(alias.start_text + ' '):
            text = text.replace(alias.start_text + ' ', '', 1)
        else:
            continue

        if alias.pattern:
            return _alias_pattern_process(alias.start_text, alias.pattern, text)
        if alias.func:
            return alias.func(text)

    return text


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
    _input_speicial_keys,
]


def thread_job_input_cmd(alias_list_, timer_list):
    global alias_list
    alias_list = alias_list_
    timer_processor = TimerProcessor(timer_list)
    kb = KBHit()

    while g_is_running.get() and not g_is_reconnect.get():
        key = kb.getch()
        if key is None:
            timer_processor.process()
            time.sleep(0.01)
            continue

        #
        special_key = kb.detect_special_key()
        if special_key:
            is_special_key = True
            key = special_key
            key_ord = None
        else:
            is_special_key = False
            key_ord = ord(key)

        for func in INPUT_FUNCTION_LIST:
            if func(key, key_ord, is_special_key):
                return

        show_input()

    kb.set_normal_term()
