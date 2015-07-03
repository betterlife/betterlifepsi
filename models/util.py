from decimal import Decimal, ROUND_HALF_UP

def format_decimal(value):
    return Decimal(value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))