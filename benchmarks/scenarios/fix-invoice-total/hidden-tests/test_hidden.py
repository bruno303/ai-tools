import unittest

from billing import calculate_invoice_total


class HiddenInvoiceTests(unittest.TestCase):
    def test_discount_rounds_up_at_half_cent(self):
        self.assertEqual(148, calculate_invoice_total([150], 1))

    def test_empty_invoice(self):
        self.assertEqual(0, calculate_invoice_total([], 25))

    def test_discount_rounds_down_below_half(self):
        self.assertEqual(148, calculate_invoice_total([149], 1))

    def test_near_threshold_rounds_up(self):
        self.assertEqual(101, calculate_invoice_total([103], 2))


if __name__ == "__main__":
    unittest.main()
