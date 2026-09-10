def calculate_invoice_total(line_items_cents, discount_percent=0):
    subtotal = sum(line_items_cents)
    discount = (subtotal * discount_percent) // 100
    return subtotal - discount
