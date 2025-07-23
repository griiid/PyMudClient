import re
import time

from pymudclient import (
    configs,
    shared_data,
)
from pymudclient.display import show_input
from pymudclient.shared_data import Status
from pymudclient.utils.kbhit import KBHit
from pymudclient.utils.print import color_print
from pymudclient.utils.telnet import send_to_host


class InputProcessor:

    ALIAS_LIST = []

    @classmethod
    def process(cls, alias_list):
        cls.ALIAS_LIST = alias_list
        kb = KBHit()

        while shared_data.CONNECT_STATUS.get() == Status.RUNNING:
            try:
                key = kb.getch()
                if key is None:
                    time.sleep(configs.THREAD_SLEEP_TIME)
                    continue

                special_key = kb.detect_special_key()
                if special_key:
                    is_special_key = True
                    key = special_key
                    key_ord = None
                else:
                    is_special_key = False
                    key_ord = ord(key)

                for func in [
                        cls._input_visible,
                        cls._input_special_keys,
                ]:
                    if func(key, key_ord, is_special_key):
                        break

                show_input()
            except Exception as e:
                import traceback
                print(traceback.format_exc())

        kb.set_normal_term()

    @classmethod
    def _input_visible(cls, key, key_ord, is_special_key):
        # special key，不在這邊處理
        if is_special_key:
            return False

        # 不是ASCII 可視字元 或 中文字
        if key_ord < 0x20 or 0x7E < key_ord < 0x4E00 or 0x9FA5 < key_ord:
            return False

        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['last_send'] = ''

            input_index = shared_data.CURRENT_INPUT['input_index']
            shared_data.CURRENT_INPUT['input'] = (
                shared_data.CURRENT_INPUT['input'][:input_index] + key +
                shared_data.CURRENT_INPUT['input'][input_index:]
            )
            shared_data.CURRENT_INPUT['input_index'] += 1

        return True

    @classmethod
    def _input_special_keys(cls, key, key_ord, is_special_key):
        # 不是 special key，不在這邊處理
        if not is_special_key:
            return False

        if key == KBHit.Key.CTRL_C:
            cls._process_ctrl_c()
        elif key == KBHit.Key.CTRL_W:
            cls._process_ctrl_w()
        elif key in {KBHit.Key.BACKSPACE, KBHit.Key.CTRL_H}:
            cls._process_backspace()
        elif key == KBHit.Key.ENTER:
            cls._process_enter()
        elif key == KBHit.Key.DELETE:
            cls._process_delete()
        elif key == KBHit.Key.RIGHT:
            cls._process_right()
        elif key == KBHit.Key.LEFT:
            cls._process_left()
        elif key == KBHit.Key.HOME:
            cls._process_home()
        elif key == KBHit.Key.END:
            cls._process_end()

        return True

    @classmethod
    def _process_ctrl_c(cls):
        shared_data.CONNECT_STATUS.set(Status.QUIT)
        color_print('\r\n$HIY$Program was interrupted$NOR$')
        return True

    @classmethod
    def _process_ctrl_w(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['last_send'] = ''
            elif shared_data.CURRENT_INPUT['input_index'] > 0:
                head_origin = shared_data.CURRENT_INPUT['input'][:shared_data.CURRENT_INPUT['input_index']]
                tail = shared_data.CURRENT_INPUT['input'][shared_data.CURRENT_INPUT['input_index']:]

                head_for_process = head_origin
                if head_for_process[-1] == ' ':
                    head_for_process = head_for_process.rstrip()

                re_match = re.search(r'(\s+)(.*)', head_for_process[::-1])
                if re_match is None:
                    head_new = ''
                else:
                    head_new = ''.join(re_match.groups())[::-1]
                shared_data.CURRENT_INPUT['input'] = head_new + tail
                shared_data.CURRENT_INPUT['input_index'] -= len(head_origin) - len(head_new)

    @classmethod
    def _process_backspace(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['last_send'] = ''
            elif shared_data.CURRENT_INPUT['input_index'] > 0:
                shared_data.CURRENT_INPUT['input'] = (
                    shared_data.CURRENT_INPUT['input'][:shared_data.CURRENT_INPUT['input_index'] - 1] +
                    shared_data.CURRENT_INPUT['input'][shared_data.CURRENT_INPUT['input_index']:]
                )
                shared_data.CURRENT_INPUT['input_index'] -= 1

    @classmethod
    def _process_enter(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['input'] = shared_data.CURRENT_INPUT['last_send']
            else:
                shared_data.CURRENT_INPUT['last_send'] = shared_data.CURRENT_INPUT['input']

            text = shared_data.CURRENT_INPUT['input']

            text = cls._alias_function(text)
            if text:
                send_to_host(text)

            shared_data.CURRENT_INPUT['input'] = ''
            shared_data.CURRENT_INPUT['input_index'] = 0

    @classmethod
    def _process_delete(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['last_send'] = ''
            else:
                shared_data.CURRENT_INPUT['input'] = (
                    shared_data.CURRENT_INPUT['input'][:shared_data.CURRENT_INPUT['input_index']] +
                    shared_data.CURRENT_INPUT['input'][shared_data.CURRENT_INPUT['input_index'] + 1:]
                )

    @classmethod
    def _process_right(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['input'] = shared_data.CURRENT_INPUT['last_send']
                shared_data.CURRENT_INPUT['input_index'] = len(shared_data.CURRENT_INPUT['last_send'])
                shared_data.CURRENT_INPUT['last_send'] = ''
            else:
                shared_data.CURRENT_INPUT['input_index'] = min(
                    len(shared_data.CURRENT_INPUT['input']), shared_data.CURRENT_INPUT['input_index'] + 1
                )

    @classmethod
    def _process_left(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['input'] = shared_data.CURRENT_INPUT['last_send']
                shared_data.CURRENT_INPUT['input_index'] = len(shared_data.CURRENT_INPUT['last_send']) - 1
                shared_data.CURRENT_INPUT['last_send'] = ''
            else:
                shared_data.CURRENT_INPUT['input_index'] = max(0, shared_data.CURRENT_INPUT['input_index'] - 1)

    @classmethod
    def _process_home(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['input'] = shared_data.CURRENT_INPUT['last_send']
                shared_data.CURRENT_INPUT['input_index'] = 0
                shared_data.CURRENT_INPUT['last_send'] = ''
            else:
                shared_data.CURRENT_INPUT['input_index'] = 0

    @classmethod
    def _process_end(cls):
        with shared_data.CURRENT_INPUT.locked():
            if shared_data.CURRENT_INPUT['last_send'] != '':
                shared_data.CURRENT_INPUT['input'] = shared_data.CURRENT_INPUT['last_send']
                shared_data.CURRENT_INPUT['input_index'] = len(shared_data.CURRENT_INPUT['last_send'])
                shared_data.CURRENT_INPUT['last_send'] = ''
            else:
                shared_data.CURRENT_INPUT['input_index'] = len(shared_data.CURRENT_INPUT['input'])

    @classmethod
    def _alias_function(cls, text):
        for alias in cls.ALIAS_LIST:
            if text == alias.start_text:
                text = ''
            elif text.startswith(alias.start_text + ' '):
                text = text.replace(alias.start_text + ' ', '', 1)
            else:
                continue

            if alias.pattern:
                return cls._alias_pattern_process(alias.pattern, text)
            if alias.func:
                return alias.func(text)

        return text

    @classmethod
    def _alias_pattern_process(cls, pattern, text):
        split_text = text.split()
        params = {}

        # variable map
        for key, value in configs.VARIABLE_MAP.items():
            pattern = pattern.replace(f'${{{key}}}', value)

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
