from pymudclient.shared_data import g_tn
from pymudclient.utils.codec import enc
from pymudclient.utils.colors import color_convert
from pymudclient.utils.print import (
    color_print,
    replace_line_print,
)


def send_to_host(text, display=True):
    try:
        if display and text != '':
            replace_line_print(f'$HIM$Send: {text}')
        g_tn.get().write(enc(text + '\r\n'))
    except BrokenPipeError as err:
        color_print(f'$HIR$輸出錯誤: {err}$NOR$')
        exit(color_convert('$HIR$輸出模式失連$NOR$'))
