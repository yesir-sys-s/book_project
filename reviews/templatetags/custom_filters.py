from django import template

register = template.Library()

@register.filter(name='repeat')
def repeat(value, times):
    """Repeats a string the specified number of times."""
    return value * int(times)
