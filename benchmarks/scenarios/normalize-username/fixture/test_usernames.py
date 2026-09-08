import unittest

from usernames import normalize_username


class NormalizeUsernameTests(unittest.TestCase):
    def test_trims_surrounding_whitespace(self):
        self.assertEqual("Alice", normalize_username("  Alice  "))


if __name__ == "__main__":
    unittest.main()
