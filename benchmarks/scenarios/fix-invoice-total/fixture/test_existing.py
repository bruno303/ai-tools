import unittest

from billing import calculate_invoice_total


class ExistingBillingTests(unittest.TestCase):
    def test_basic_total(self):
        self.assertEqual(1250, calculate_invoice_total([500, 750]))

    def test_existing_exact_discount(self):
        self.assertEqual(900, calculate_invoice_total([1000], 10))

    def test_discount_half_cent_rounds_up(self):
        self.assertEqual(247, calculate_invoice_total([250], 1))


if __name__ == "__main__":
    unittest.main()
