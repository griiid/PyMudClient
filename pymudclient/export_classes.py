from dataclasses import dataclass
from typing import Callable


@dataclass
class Alias:

    start_text: str
    pattern: str | None = None
    func: Callable | None = None


@dataclass
class Trigger:

    pattern: str
    data: str | None = None
    func: Callable | None = None


@dataclass
class Timer:

    seconds: int
    data: str | None = None
    func: Callable | None = None
