from decimal import Decimal, ROUND_HALF_UP


def format_decimal(value):
    """
    Format a decimal with two decimal point with rounding mode ROUND_HALF_UP
    :param value the decimal to format
    """
    return Decimal(Decimal(value).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
