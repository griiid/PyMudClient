import telnetlib
import threading
import time

from .input_cmd import thread_job_input_cmd
from .recv import thread_job_recv
from .shared_data import (
    g_is_reconnect,
    g_is_running,
    g_tn,
)
from .utils.print import color_print


def excepthook(args):
    color_print(f'$HIR$Threading.excepthook: {args}$NOR$')
    g_is_reconnect.set(True)


def login(host, port):
    time.sleep(0.3)
    try_start = time.time()
    while True:
        time.sleep(0.1)
        if time.time() - try_start < 3:
            try:
                color_print(f'開始嘗試連線至 $HIY${host}:{port}$NOR$', flush=True)
                g_tn.set(telnetlib.Telnet(host, port))
                break
            except Exception:
                color_print('$HIR$連線失敗，三秒內將繼續重試$NOR$', flush=True)
                time.sleep(3)
                continue
        else:
            color_print('$HIR$連線有誤，十秒後再次嘗試$NOR$', flush=True)
            time.sleep(10)
            try_start = time.time()


def thread_start(alias_list, trigger_list, timer_list):
    g_is_reconnect.set(False)

    thread_func_list = [
        (thread_job_input_cmd, [alias_list, timer_list]),
        (thread_job_recv, [trigger_list]),
    ]
    thread_list = []

    for func, args in thread_func_list:
        thread = threading.Thread(target=func, args=args)
        thread_list.append((thread, func.__name__))
        thread.start()

    return thread_list


def thread_wait_close(thread_list):
    color_print(f'$HIY$等待 {len(thread_list)} 個 thread 關閉...$NOR$')
    for thread, name in thread_list:
        thread.join()
        color_print(f'$CYN${name}$NOR$ 已關閉')
    thread_list.clear()


class Status:
    START = 0
    RUNNING = 1
    QUIT = 2


def mud_run(host, port, alias_list=None, trigger_list=None, timer_list=None):
    threading.excepthook = excepthook
    status = Status.START

    if alias_list is None:
        alias_list = []
    if trigger_list is None:
        trigger_list = []
    if timer_list is None:
        timer_list = []

    while True:
        try:
            time.sleep(0.5)

            if status == Status.START:
                login(host, port)
                thread_list = thread_start(alias_list, trigger_list, timer_list)
                status = Status.RUNNING
            elif status == Status.QUIT:
                g_is_running.set(False)
                color_print('$HIY$關閉程式$NOR$')
                thread_wait_close(thread_list)
                break

            if not g_is_running.get():
                status = Status.QUIT
                continue

            if g_is_reconnect.get():
                status = Status.START
                color_print('$HIY$等待重新連線...$NOR$', flush=True)

                try:
                    g_tn.get().close()
                except Exception as e:
                    color_print(f'$HIR$Telnet close error: {e}$NOR$')
                    status = Status.QUIT
                    continue

                thread_wait_close(thread_list)

                # 倒數 3 秒
                for i in range(3, 0, -1):
                    color_print(f'$HIY${i}...$NOR$')
                    time.sleep(1)
        except KeyboardInterrupt:
            status = Status.QUIT
            continue
