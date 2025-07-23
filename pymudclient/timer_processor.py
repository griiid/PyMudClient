import time
from dataclasses import dataclass
from typing import Callable

from pymudclient import shared_data
from pymudclient.shared_data import Status
from pymudclient.utils.telnet import send_to_host


class TimerProcessor:

    TIMER_LIST = []

    @dataclass
    class _Timer:

        seconds: int
        last_time: int
        data: str = None
        func: Callable = None

    @classmethod
    def process(cls, timer_list):
        start_time = time.time()
        cls.TIMER_LIST = [cls._Timer(timer.seconds, start_time, timer.data, timer.func) for timer in timer_list]

        while shared_data.CONNECT_STATUS.get() == Status.RUNNING:
            for timer in cls.TIMER_LIST:
                if time.time() - timer.last_time >= timer.seconds:
                    timer.last_time = time.time()

                    if timer.data:
                        send_to_host(timer.data)
                    elif timer.func:
                        text = timer.func()
                        if text:
                            send_to_host(text)

            time.sleep(0.001)
