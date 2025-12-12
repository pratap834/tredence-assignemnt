example_code = """
def calculate_total(price, quantity, tax_rate, discount, shipping, handling_fee):
    subtotal = price * quantity
    tax = subtotal * tax_rate
    total = subtotal + tax - discount + shipping + handling_fee
    return total

def process_order(order_id, customer_name, items, payment_method, delivery_address, notes):
    if not order_id:
        return None
    
    total = 0
    for item in items:
        item_total = item['price'] * item['quantity']
        total += item_total
    
    if payment_method == 'credit':
        total = total * 1.02
    
    return {
        'order_id': order_id,
        'customer': customer_name,
        'total': total,
        'payment': payment_method
    }

def validate_input(data):
    if not data:
        return False
    if len(data) < 5:
        return False
    return True
"""

if __name__ == "__main__":
    print("Example code for testing:")
    print(example_code)
