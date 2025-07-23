from pymudclient import shared_data
from pymudclient.utils.print import (
    move_cursor_to_index,
    replace_line_print,
)


def show_input():
    '''將目前為止輸入的字顯示在畫面上'''

    with shared_data.CURRENT_INPUT.locked():
        if shared_data.CURRENT_INPUT['last_send'] != '':
            replace_line_print(
                f'\x1B[30;47m{shared_data.CURRENT_INPUT["last_send"]}\x1B[m',
                end='\r',
                flush=True,
                color=False,
            )
        else:
            replace_line_print(
                f'{shared_data.CURRENT_INPUT["input"]}',
                end='\r',
                flush=True,
                color=False,
            )
            move_cursor_to_index()
