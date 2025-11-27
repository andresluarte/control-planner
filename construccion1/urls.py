from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import FileResponse, Http404
import os
from construccion1app import views

# Vista para servir el Service Worker
def serve_sw(request):
    sw_path = os.path.join(settings.BASE_DIR, 'firebase-messaging-sw.js')
    if os.path.exists(sw_path):
        response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
        response['Service-Worker-Allowed'] = '/'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    raise Http404("Service Worker not found")

# Vista para servir el manifest.json
def serve_manifest(request):
    manifest_path = os.path.join(settings.BASE_DIR, 'manifest.json')
    if os.path.exists(manifest_path):
        return FileResponse(open(manifest_path, 'rb'), content_type='application/json')
    raise Http404("Manifest not found")

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de tu app
    path('', include('construccion1app.urls')),
    
    # PWA y Firebase
    path('firebase-messaging-sw.js', serve_sw, name='firebase-sw'),
    path('manifest.json', serve_manifest, name='manifest'),
    path('save-fcm-token/', views.save_fcm_token, name='save_fcm_token'), 
    # ... tus otras rutas
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
