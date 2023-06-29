from dataclasses import dataclass
from typing import Callable

from .mud import mud_run as run


@dataclass
class Alias:

    start_text: str
    pattern: str = None
    func: Callable = None


@dataclass
class Trigger:

    pattern: str
    data: str = None
    func: Callable = None


@dataclass
class Timer:

    seconds: int
    data: str = None
    func: Callable = None
