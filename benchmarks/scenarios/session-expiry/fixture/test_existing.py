import unittest
from datetime import datetime, timezone

from auth import SessionAuth
from clock import Clock
from store import SessionStore


class ExistingSessionTests(unittest.TestCase):
    def test_recent_session_is_valid(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        auth = SessionAuth(SessionStore(), Clock(now))
        auth.create("s1", now)
        self.assertFalse(auth.is_expired("s1"))


if __name__ == "__main__":
    unittest.main()
