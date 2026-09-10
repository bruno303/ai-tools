import unittest

from ratelimit import SlidingWindowLimiter


class HiddenSlidingWindowTests(unittest.TestCase):
    def test_oldest_request_refills_gradually(self):
        now = [0]
        limiter = SlidingWindowLimiter(2, 10, lambda: now[0])
        self.assertTrue(limiter.allow("a"))
        now[0] = 5
        self.assertTrue(limiter.allow("a"))
        now[0] = 9
        self.assertFalse(limiter.allow("a"))
        now[0] = 10
        self.assertTrue(limiter.allow("a"))
        now[0] = 15
        self.assertTrue(limiter.allow("a"))

    def test_keys_are_independent_and_clock_is_deterministic(self):
        now = [100]
        limiter = SlidingWindowLimiter(1, 20, lambda: now[0])
        self.assertTrue(limiter.allow("a"))
        self.assertTrue(limiter.allow("b"))
        self.assertFalse(limiter.allow("a"))
        now[0] = 120
        self.assertTrue(limiter.allow("a"))


if __name__ == "__main__":
    unittest.main()
