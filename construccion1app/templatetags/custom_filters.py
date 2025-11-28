from django import template
import os 
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a un valor de diccionario en templates"""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return ""


@register.filter
def basename(value):
    """Devuelve solo el nombre del archivo sin la ruta"""
    return os.path.basename(str(value))
