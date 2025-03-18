from django import template
import locale
from decimal import Decimal

register = template.Library()

@register.filter(name='indian_currency')
def indian_currency(value):
    """
    Format a number as Indian currency (₹) with proper thousands separators.
    Example: 123456.78 becomes ₹1,23,456.78
    """
    if value is None:
        return "₹0.00"
    
    try:
        # Convert to Decimal for accurate decimal handling
        value = Decimal(str(value))
        
        # Format with 2 decimal places
        formatted_value = '{:.2f}'.format(value)
        
        # Split into integer and decimal parts
        int_part, decimal_part = formatted_value.split('.')
        
        # Format integer part with Indian thousands separators
        # First, reverse the string to process from right to left
        int_part_reversed = int_part[::-1]
        
        # Add commas: first after 3 digits, then after every 2 digits
        groups = []
        for i in range(0, len(int_part_reversed), 2):
            if i == 0:
                # First group is 3 digits
                groups.append(int_part_reversed[i:i+3])
            else:
                # Subsequent groups are 2 digits
                groups.append(int_part_reversed[i:i+2])
        
        # Join with commas, then reverse back
        formatted_int = ','.join(groups)[::-1]
        
        # Combine with decimal part and add rupee symbol
        return f"₹{formatted_int}.{decimal_part}"
    except (ValueError, TypeError):
        return f"₹{value}"

@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiply the value by the argument
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 