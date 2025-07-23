import re
import time

from pymudclient import (
    configs,
    shared_data,
)
from pymudclient.display import show_input
from pymudclient.shared_data import Status
from pymudclient.utils.print import (
    color_print,
    replace_line_print,
)
from pymudclient.utils.telnet import send_to_host


class RecvProcessor:

    @classmethod
    def process(cls, trigger_list, pre_process_recv_content_func):
        while shared_data.CONNECT_STATUS.get() == Status.RUNNING:
            try:
                with shared_data.TN.locked():
                    # 如果有資料，就在 0.1 秒內一直讀取，把這次 server 傳來的資料收完
                    data = shared_data.TN.get().read_very_eager()
                    if not data:
                        continue

                    start_time = time.time()
                    while time.time() - start_time < 0.1:
                        data += shared_data.TN.get().read_very_eager()
                        time.sleep(configs.THREAD_SLEEP_TIME)

                if pre_process_recv_content_func is not None:
                    new_data = pre_process_recv_content_func(data)
                    if new_data is not None:
                        data = new_data

                data = shared_data.TN.get().re_decode(data)
                content_list = data.split('\r\n')

                for content in content_list:
                    replace_line_print(content)

                    cls._triggers(trigger_list, content)

                show_input()

            except EOFError:
                color_print('$HIR$Monitor mode error$NOR$')
                shared_data.CONNECT_STATUS.set(Status.RECONNECT)

            except OSError:
                color_print('$HIR$Cannot connect$NOR$')
                shared_data.CONNECT_STATUS.set(Status.RECONNECT)

            except Exception:
                # TODO: 使用 logging 決定要不要印出 debug 資訊
                import traceback
                print(traceback.format_exc())

    @classmethod
    def _triggers(cls, trigger_list, content=''):
        if not trigger_list:
            return

        content_text_only = re.compile(r'\x1b\[[^m]*m').sub('', content).lstrip('> ').rstrip()

        for trigger in trigger_list:
            match = re.search(trigger.pattern, content_text_only)
            if not match:
                continue

            if trigger.data is not None:
                send_to_host(trigger.data)
            elif trigger.func is not None:
                data = trigger.func(content_text_only, match.groups())
                if data is not None:
                    send_to_host(data)
