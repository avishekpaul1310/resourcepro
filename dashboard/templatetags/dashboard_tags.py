import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def jsonify(obj):
    """Convert object to JSON string for use in JavaScript"""
    return mark_safe(json.dumps(obj))

@register.filter  
def mul(value, multiplier):
    """Multiply a value by a multiplier"""
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_class(field, css_class):
    """Add CSS class to form field"""
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field
