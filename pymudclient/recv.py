import re
import time

from pymudclient.display import show_input
from pymudclient.shared_data import (
    g_is_reconnect,
    g_is_running,
    g_tn,
)
from pymudclient.utils.codec import (
    dec,
    enc,
)
from pymudclient.utils.colors import (
    color_convert,
    remove_strange_color_code,
)
from pymudclient.utils.print import (
    color_print,
    replace_line_print,
)
from pymudclient.utils.telnet import send_to_host

ansi_escape = re.compile(r'\x1b\[[^m]*m')


def _triggers(trigger_list, content=''):
    if not trigger_list:
        return

    content_text_only = ansi_escape.sub('', content).lstrip('> ').rstrip()

    for trigger in trigger_list:
        match = re.search(trigger.pattern, content_text_only)
        if not match:
            continue

        if trigger.data is not None:
            send_to_host(trigger.data, display=False)
        elif trigger.func is not None:
            data = trigger.func(content_text_only, match.groups())
            if data is not None:
                send_to_host(data, display=False)


IGNORE_LINES = []


def thread_job_recv(trigger_list):
    while g_is_running.get() and not g_is_reconnect.get():
        try:
            data = g_tn.get().read_very_eager()
            if not data:
                continue

            last_time = time.time()
            while time.time() - last_time < 0.1:
                data += g_tn.get().read_very_eager()
                time.sleep(0.01)

            data = remove_strange_color_code(data)
            content_list = dec(data).split('\r\n')

            for content in content_list:
                content = dec(enc(content))
                replace_line_print(content)

                _triggers(trigger_list, content)

            show_input()

        except EOFError:
            color_print('$HIR$監測模式失連$NOR$')
            g_is_reconnect.set(True)
        except OSError:
            color_print(color_convert('$HIR$無法連線$NOR$'))
            g_is_reconnect.set(True)
