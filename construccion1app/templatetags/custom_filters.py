from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a un valor de diccionario en templates"""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return ""
