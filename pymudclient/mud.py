import threading
import time

from pymudclient import (
    configs,
    shared_data,
)
from pymudclient.input_processor import InputProcessor
from pymudclient.recv_processor import RecvProcessor
from pymudclient.shared_data import Status
from pymudclient.utils.print import color_print
from pymudclient.utils.telnet import TelnetClient


class PyMudClient:

    def __init__(
        self,
        host,
        port,
        account=None,
        password=None,
        alias_list=None,
        trigger_list=None,
        timer_list=None,
        variable_map=None,
        pre_process_recv_content_func=None,
        encoding='latin1',
    ):
        self.host = host
        self.port = port

        self.alias_list = [] if alias_list is None else alias_list
        self.trigger_list = [] if trigger_list is None else trigger_list
        self.timer_list = [] if timer_list is None else timer_list

        self.pre_process_recv_content_func = pre_process_recv_content_func

        self._thread_list = []

        shared_data.CONNECT_STATUS.set(Status.QUIT)

        configs.VARIABLE_MAP = {} if variable_map is None else variable_map
        if account is not None:
            configs.VARIABLE_MAP['ACCOUNT'] = account
        if password is not None:
            configs.VARIABLE_MAP['PASSWORD'] = password

        configs.ENCODING = encoding

    @property
    def alias_list(self):
        return self._alias_list

    @alias_list.setter
    def alias_list(self, value):
        self._alias_list = [] if value is None else value

    @property
    def trigger_list(self):
        return self._trigger_list

    @trigger_list.setter
    def trigger_list(self, value):
        self._trigger_list = [] if value is None else value

    @property
    def timer_list(self):
        return self._timer_list

    @timer_list.setter
    def timer_list(self, value):
        self._timer_list = [] if value is None else value

    def run(self):
        shared_data.CONNECT_STATUS.set(Status.START)

        while True:
            try:
                time.sleep(0.1)

                if shared_data.CONNECT_STATUS.get() == Status.START:
                    self._connect()
                    shared_data.CONNECT_STATUS.set(Status.RUNNING)
                    self._thread_start()

                elif shared_data.CONNECT_STATUS.get() == Status.QUIT:
                    color_print('$HIY$Closing program...$NOR$')
                    self._thread_wait_close()
                    break

                elif shared_data.CONNECT_STATUS.get() == Status.RECONNECT:
                    color_print('$HIY$Waiting for reconnect...$NOR$')

                    try:
                        shared_data.TN.get().close()
                    except Exception as e:
                        color_print(f'$HIR$Telnet close error: {e}$NOR$')
                        shared_data.CONNECT_STATUS.set(Status.QUIT)
                        continue

                    self._thread_wait_close()

                    # 倒數 3 秒
                    for i in range(3, 0, -1):
                        color_print(f'$HIY${i}...$NOR$')
                        time.sleep(1)

                    shared_data.CONNECT_STATUS.set(Status.START)

            except KeyboardInterrupt:
                shared_data.CONNECT_STATUS.set(Status.QUIT)
                continue

    def _connect(self):
        start_time = time.time()

        while True:
            time.sleep(0.1)

            if time.time() - start_time < 3:
                try:
                    color_print(f'Connecting to $HIY${self.host}:{self.port}$NOR$', flush=True)
                    tn = TelnetClient(self.host, self.port, encoding=configs.ENCODING)
                    shared_data.TN.set(tn)
                    color_print('$HIY$Connected$NOR$')
                    break
                except Exception:
                    color_print('$HIR$Connect failed, will try again after 3 seconds$NOR$', flush=True)
                    time.sleep(3)
                    continue
            else:
                color_print('$HIR$Connect failed, will try again after 10 seconds$NOR$', flush=True)
                time.sleep(10)
                start_time = time.time()

    def _thread_start(self):
        thread_func_list = [
            (InputProcessor.process, [self.alias_list, self.timer_list]),
            (RecvProcessor.process, [self.trigger_list, self.pre_process_recv_content_func]),
        ]
        self._thread_list = []

        for func, args in thread_func_list:
            thread = threading.Thread(target=func, args=args)
            self._thread_list.append((thread, func.__qualname__))
            thread.start()

    def _thread_wait_close(self):
        if not self._thread_list:
            return

        color_print(f'$HIY$Waiting for {len(self._thread_list)} threads to close...$NOR$')
        for thread, name in self._thread_list:
            thread.join()
            color_print(f'Thread $CYN${name}$NOR$ Closed')

        self._thread_list = []
