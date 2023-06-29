import re

from .display import show_input
from .shared_data import (
    g_is_reconnect,
    g_is_running,
    g_tn,
)
from .utils.codec import (
    dec,
    enc,
)
from .utils.colors import (
    color_convert,
    remove_strange_color_code,
)
from .utils.print import (
    color_print,
    replace_line_print,
)
from .utils.telnet import send_to_host

ansi_escape = re.compile(r'\x1b\[[^m]*m')


def _triggers(trigger_list, content=''):
    if not trigger_list:
        return

    content_text_only = ansi_escape.sub('', content).lstrip('> ').rstrip()

    for trigger in trigger_list:
        match = re.search(trigger.pattern, content_text_only)
        if not match:
            continue

        if trigger.data:
            send_to_host(trigger.data, display=False)
        elif trigger.func:
            data = trigger.func(match.groups())
            if data:
                send_to_host(data, display=False)


IGNORE_LINES = []


def thread_job_recv(trigger_list):
    while g_is_running.get() and not g_is_reconnect.get():
        try:
            data = g_tn.get().read_very_eager()
            if not data:
                continue

            data = remove_strange_color_code(data)
            content_list = dec(data).split('\r\n')

            for content in content_list:
                # TODO: 用 regex 取代這些無用的行
                if content == '' or content == '\x1B[2;37;0m' or content == '\x1B[2;37;0m> ' or content == '> ':
                    continue

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
