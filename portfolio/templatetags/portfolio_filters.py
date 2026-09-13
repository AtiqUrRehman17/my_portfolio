from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Split a string by the given delimiter"""
    if value:
        return value.split(arg)
    return []

@register.filter(name='truncatewords')
def truncatewords(value, arg):
    """Truncate text to specified number of words"""
    if value:
        words = value.split()
        if len(words) > int(arg):
            return ' '.join(words[:int(arg)]) + '...'
    return value