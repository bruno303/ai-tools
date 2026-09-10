import unittest
from datetime import datetime, timedelta, timezone

from auth import SessionAuth
from clock import Clock
from store import SessionStore


class HiddenSessionTests(unittest.TestCase):
    def test_exactly_thirty_minutes_is_expired(self):
        start = datetime(2026, 1, 1, 12)
        auth = SessionAuth(SessionStore(), Clock(start + timedelta(minutes=30)))
        auth.create("s1", start)
        self.assertTrue(auth.is_expired("s1"))

    def test_naive_and_aware_timestamps_compare_consistently(self):
        start = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        auth = SessionAuth(SessionStore(), Clock(start + timedelta(minutes=29)))
        auth.create("s1", start.replace(tzinfo=None))
        self.assertFalse(auth.is_expired("s1"))

    def test_missing_session_is_expired(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        self.assertTrue(SessionAuth(SessionStore(), Clock(now)).is_expired("none"))


if __name__ == "__main__":
    unittest.main()
