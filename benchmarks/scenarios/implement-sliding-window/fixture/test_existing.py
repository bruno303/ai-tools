import unittest

from ratelimit import FixedWindowLimiter, SlidingWindowLimiter


class ExistingRateLimitTests(unittest.TestCase):
    def test_fixed_window_is_unchanged(self):
        now = [0]
        limiter = FixedWindowLimiter(2, 10, lambda: now[0])
        self.assertTrue(limiter.allow("a"))
        self.assertTrue(limiter.allow("a"))
        self.assertFalse(limiter.allow("a"))
        now[0] = 10
        self.assertTrue(limiter.allow("a"))

    def test_sliding_scaffold_contract(self):
        now = [0]
        limiter = SlidingWindowLimiter(2, 10, lambda: now[0])
        self.assertTrue(limiter.allow("a"))
        self.assertTrue(limiter.allow("a"))
        self.assertFalse(limiter.allow("a"))


if __name__ == "__main__":
    unittest.main()
