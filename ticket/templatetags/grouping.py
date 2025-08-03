from django import template

register = template.Library()

@register.filter
def grouped(value, n):
    """
    Groups a list into chunks of size n.
    Usage: {% for row in seats|grouped:4 %}
    """
    return [value[i:i + n] for i in range(0, len(value), n)]
