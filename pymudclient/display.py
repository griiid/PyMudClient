from pymudclient.shared_data import g_input
from pymudclient.utils.print import (
    move_cursor_to_index,
    replace_line_print,
)


def show_input():
    '''將目前為止輸入的字顯示在畫面上'''

    if g_input['last_send'] != '':
        replace_line_print(f'\x1B[30;47m{g_input["last_send"]}\x1B[m', end='\r', flush=True, color=False)
    else:
        replace_line_print(f'{g_input["input"]}', end='\r', flush=True, color=False)
        move_cursor_to_index()
