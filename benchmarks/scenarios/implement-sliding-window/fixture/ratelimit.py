from collections import defaultdict, deque


class FixedWindowLimiter:
    def __init__(self, limit, window_seconds, clock):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self._windows = defaultdict(lambda: [None, 0])

    def allow(self, key):
        now = self.clock()
        window = int(now // self.window_seconds)
        state = self._windows[key]
        if state[0] != window:
            state[:] = [window, 0]
        if state[1] >= self.limit:
            return False
        state[1] += 1
        return True


class SlidingWindowLimiter:
    """Scaffold for a limiter that counts requests in a rolling window."""

    def __init__(self, limit, window_seconds, clock):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self._requests = defaultdict(deque)

    def allow(self, key):
        raise NotImplementedError
