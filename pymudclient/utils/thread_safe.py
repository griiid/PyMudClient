import threading
from contextlib import contextmanager
from typing import (
    Any,
    Generic,
    TypeVar,
)

T = TypeVar('T')


class ThreadSafe(Generic[T]):

    def __init__(self, value: T):
        self._value = value
        self._lock = threading.RLock()

    def __getattr__(self, name: str) -> Any:
        with self._lock:
            return getattr(self._value, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ('_value', '_lock'):
            super().__setattr__(name, value)
        else:
            with self._lock:
                setattr(self._value, name, value)

    def __getitem__(self, key: Any) -> Any:
        with self._lock:
            return self._value[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        with self._lock:
            self._value[key] = value

    def set(self, new_value: T) -> None:
        with self._lock:
            self._value = new_value

    def get(self) -> T:
        with self._lock:
            return self._value

    @contextmanager
    def locked(self):
        with self._lock:
            yield self


# Example usage:
if __name__ == '__main__':

    class MyClass:

        def __init__(self):
            self.value = 0

        def say_hello(self):
            print('Hello!')

    # Test dictionary
    dict_data = ThreadSafe[dict]({})
    dict_data['a'] = 123
    dict_data['b'] = 456
    print(dict_data.get())    # Output: {'a': 123, 'b': 456}

    # Test integer
    int_data = ThreadSafe[int](100)
    int_data.set(200)
    new_number = int_data.get() + 23
    print(int_data.get())    # Output: 200

    # Test custom class
    my_class_data = ThreadSafe[MyClass](MyClass())
    my_class_data.value = 100
    my_class_data.say_hello()    # Output: Hello!
    print(my_class_data.value)    # Output: 100
    my_class_data.set(MyClass())
    print(my_class_data.value)    # Output: 0
