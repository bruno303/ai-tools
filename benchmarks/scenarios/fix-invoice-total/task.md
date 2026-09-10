# Task: fix invoice total rounding

The billing code returns incorrect totals for some discounted invoices because
the discount is truncated instead of rounded.

Update `calculate_invoice_total` so it sums line items in integer cents, rounds
the percentage discount half-up to the nearest cent, and then subtracts that
discount from the subtotal. Preserve the public function signature and make
empty invoices and zero discounts behave sensibly. Do not use floating point
money arithmetic.
