import threading


class _ThreadSafeData:

    def __init__(self, data):
        self.data = data
        self.lock = threading.Lock()

    def get(self):
        with self.lock:
            return self.data

    def set(self, value):
        with self.lock:
            self.data = value


class _ThreadSafeDict:

    def __init__(self, data):
        self.data = data
        self.lock = threading.Lock()

    def __getitem__(self, key):
        with self.lock:
            return self.data.get(key)

    def __setitem__(self, key, value):
        with self.lock:
            self.data[key] = value


g_tn = _ThreadSafeData(None)
g_is_running = _ThreadSafeData(True)
g_is_reconnect = _ThreadSafeData(False)
g_input = _ThreadSafeDict({
    'input': '',
    'input_index': 0,
    'last_send': '',
})
