import unittest
from datetime import datetime

from consumer import date_label, read_timestamp
from helpers import format_datetime, parse_date


class ExistingDatetimeTests(unittest.TestCase):
    def test_consumer_uses_public_helpers(self):
        value = datetime(2026, 2, 3, 4, 5, 6)
        self.assertEqual("2026-02-03", date_label(value))
        self.assertEqual(value, read_timestamp("2026-02-03T04:05:06"))

    def test_existing_helpers(self):
        self.assertEqual("2026-02-03T04:05:06", format_datetime(datetime(2026, 2, 3, 4, 5, 6)))
        self.assertEqual(datetime(2026, 2, 3).date(), parse_date("2026-02-03"))


if __name__ == "__main__":
    unittest.main()
