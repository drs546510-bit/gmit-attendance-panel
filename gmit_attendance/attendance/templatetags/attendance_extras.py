from django import template

register = template.Library()


@register.filter
def dictfetch(d, key):
    """Usage: {{ some_dict|dictfetch:key }} — looks up key in a dict from a template."""
    if not d:
        return ''
    return d.get(key, '')
