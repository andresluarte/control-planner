from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def puede_agregar_actividad(total_incidencia):
    """Determina si se puede agregar una actividad basado en la incidencia total"""
    return float(total_incidencia) < 99.95