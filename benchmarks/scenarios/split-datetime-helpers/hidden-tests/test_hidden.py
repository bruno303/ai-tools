import unittest
from datetime import datetime

from helpers import format_date, format_datetime, parse_date, parse_datetime


class HiddenDatetimeTests(unittest.TestCase):
    def test_split_modules_and_compatibility_exports(self):
        from helpers.format import format_date as split_format_date
        from helpers.format import format_datetime as split_format_datetime
        from helpers.parse import parse_date as split_parse_date
        from helpers.parse import parse_datetime as split_parse_datetime

        value = datetime(2024, 2, 29, 23, 59, 58)
        self.assertEqual(format_date(value), split_format_date(value))
        self.assertEqual(format_datetime(value), split_format_datetime(value))
        self.assertEqual(parse_date("2024-02-29"), split_parse_date("2024-02-29"))
        self.assertEqual(parse_datetime("2024-02-29T23:59:58"), split_parse_datetime("2024-02-29T23:59:58"))

    def test_round_trips_and_edge_inputs(self):
        value = datetime(2000, 1, 1, 0, 0, 0)
        self.assertEqual(value.date(), parse_date(format_date(value)))
        self.assertEqual(value, parse_datetime(format_datetime(value)))


if __name__ == "__main__":
    unittest.main()
