# portal/templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key.
    Usage: {{ row|get_item:col }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, "N/A")
    return "N/A"


@register.filter
def endswith(value, arg):
    """
    Check if string ends with substring.
    Usage: {% if col|endswith:"_time" %}
    """
    return str(value).endswith(str(arg))


@register.filter
def multiply(value, arg):
    """
    Multiply value by argument.
    Usage: {{ value|multiply:100 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def format_duration(minutes):
    """
    Format duration in minutes to human-readable format.
    Usage: {{ duration_minutes|format_duration }}
    """
    try:
        mins = float(minutes)
        if mins < 60:
            return f"{mins:.0f}m"
        hours = int(mins // 60)
        remaining_mins = int(mins % 60)
        if remaining_mins == 0:
            return f"{hours}h"
        return f"{hours}h {remaining_mins}m"
    except (ValueError, TypeError):
        return "-"


@register.filter
def divide(value, arg):
    """
    Divide value by argument.
    Usage: {{ value|divide:total }}
    """
    try:
        divisor = float(arg)
        if divisor == 0:
            return 0
        return float(value) / divisor
    except (ValueError, TypeError):
        return 0