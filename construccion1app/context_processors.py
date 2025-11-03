# construccion1app/context_processors.py
from .models import Notificacion

def notificaciones_context(request):
    if request.user.is_authenticated:
        notificaciones_no_leidas = request.user.notificaciones.filter(leida=False).count()
    else:
        notificaciones_no_leidas = 0
    return {"notificaciones_no_leidas": notificaciones_no_leidas}
from django.conf import settings

def webpush_settings(request):
    return {
        'WEBPUSH_SETTINGS': settings.WEBPUSH_SETTINGS
    }
from django.conf import settings

def webpush_vapid(request):
    return {
        'VAPID_PUBLIC_KEY': settings.WEBPUSH_SETTINGS['VAPID_PUBLIC_KEY']
    }