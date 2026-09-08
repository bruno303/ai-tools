import unittest

from usernames import normalize_username


class HiddenNormalizeUsernameTests(unittest.TestCase):
    def test_lowercases_username(self):
        self.assertEqual("alice", normalize_username("Alice"))

    def test_trims_and_lowercases_together(self):
        self.assertEqual("alice", normalize_username("  ALICE  "))

    def test_rejects_empty_username(self):
        with self.assertRaises(ValueError):
            normalize_username("   ")


if __name__ == "__main__":
    unittest.main()
