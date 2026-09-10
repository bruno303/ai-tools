from datetime import datetime, timezone


class Clock:
    def __init__(self, current):
        self.current = current

    def now(self):
        return self.current


def utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
