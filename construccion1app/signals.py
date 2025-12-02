from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Actividad, Notificacion, Usuario
from django.urls import reverse
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, messaging
import os
import json
import base64

# Inicializar Firebase Admin SDK solo una vez
if not firebase_admin._apps:
    try:
        firebase_env = os.environ.get("FIREBASE_CREDENTIALS")
        if firebase_env:
            print("🔐 Usando credenciales desde variable de entorno (base64)")
            decoded_bytes = base64.b64decode(firebase_env)
            cred_dict = json.loads(decoded_bytes)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase inicializado desde variable de entorno")
        else:
            cred_path = os.path.join(settings.BASE_DIR, "credentials", "firebase-key.json")
            if os.path.exists(cred_path):
                print("📁 Usando credenciales desde archivo local")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase inicializado desde archivo local")
            else:
                print("⚠️ No se encontraron credenciales de Firebase en ninguna fuente")
    except Exception as e:
        print(f"❌ Error al inicializar Firebase: {e}")
        import traceback
        traceback.print_exc()


def enviar_notificacion_push(titulo, mensaje_texto, token, usuario=None, url=None):
    """Envía una notificación push usando Firebase Cloud Messaging HTTP v1"""
    print(f"🔔 INTENTANDO ENVIAR NOTIFICACIÓN")
    print(f"   Título: {titulo}")
    print(f"   Mensaje: {mensaje_texto}")
    print(f"   Token: {token[:30] if token else 'NINGUNO'}...")
    print(f"   URL: {url}")
    
    try:
        webpush_config = messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                icon="/static/construccion1app/img/logo3.png",
                badge="/static/construccion1app/img/logo3.png",
                vibrate=[200, 100, 200]
            )
        )
        
        if not settings.DEBUG and url:
            webpush_config.fcm_options = messaging.WebpushFCMOptions(link=url)
            print(f"   ✅ Link agregado (producción): {url}")
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=titulo,
                body=mensaje_texto,
            ),
            token=token,
            webpush=webpush_config
        )
        
        response = messaging.send(message)
        print(f"✅ Push enviado exitosamente: {response}")
        return response
        
    except messaging.UnregisteredError as e:
        print(f"❌ Token no registrado o expirado: {e}")
        
        # LIMPIAR TOKEN EXPIRADO
        if usuario:
            print(f"🧹 Limpiando token expirado de {usuario.email}")
            usuario.fcm_token = None
            usuario.save(update_fields=['fcm_token'])
            print(f"✅ Token limpiado, usuario deberá renovarlo en próximo login")
        
        return None
        
    except messaging.InvalidArgumentError as e:
        print(f"❌ Argumento inválido en mensaje: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    except Exception as e:
        print(f"❌ ERROR enviando push FCM:")
        import traceback
        traceback.print_exc()
        return None
    



# ----------------------------- 
# PRE_SAVE: GUARDAR ESTADO ANTERIOR
# ----------------------------- 
@receiver(pre_save, sender=Actividad)
def guardar_estado_anterior(sender, instance, **kwargs):
    """Guarda el estado anterior de la actividad para detectar cambios"""
    if instance.pk:
        try:
            anterior = Actividad.objects.get(pk=instance.pk)
            instance._asignado_anterior = anterior.asignado
            instance._avance_anterior = anterior.avance
            instance._estado_anterior = anterior.estado_ejecucion
            instance._asignacion_anterior = anterior.estado_asignacion
        except Actividad.DoesNotExist:
            instance._asignado_anterior = None
            instance._avance_anterior = None
            instance._estado_anterior = None
            instance._asignacion_anterior = None
    else:
        instance._asignado_anterior = None
        instance._avance_anterior = None
        instance._estado_anterior = None
        instance._asignacion_anterior = None


# ----------------------------- 
# POST_SAVE: LÓGICA UNIFICADA DE NOTIFICACIONES
# ----------------------------- 
@receiver(post_save, sender=Actividad)
def notificacion_actividad_unificada(sender, instance, created, **kwargs):
    """
    Signal unificado que maneja TODAS las notificaciones de actividades
    Mensajes detallados con información completa de la actividad
    """
    print(f"\n{'='*60}")
    print(f"🔔 SIGNAL UNIFICADO: notificacion_actividad_unificada")
    print(f" Created: {created}")
    print(f" Actividad: {instance.nombre}")
    print(f" Asignado: {instance.asignado}")
    
    # Recuperar estados anteriores
    asignado_anterior = getattr(instance, '_asignado_anterior', None)
    avance_anterior = getattr(instance, '_avance_anterior', None)
    estado_anterior = getattr(instance, '_estado_anterior', None)
    asignacion_anterior = getattr(instance, '_asignacion_anterior', None)
    
    print(f" Asignado anterior: {asignado_anterior}")
    print(f" Avance: {avance_anterior} → {instance.avance}")
    print(f" Estado ejecución: {estado_anterior} → {instance.estado_ejecucion}")
    print(f" Estado asignación: {asignacion_anterior} → {instance.estado_asignacion}")
    
    # Información detallada de la actividad (usado en todos los mensajes)
    detalle_actividad = (
        f"la actividad '{instance.nombre}' "
        f"del espacio {instance.espacio.nombre} "
        f"del nivel {instance.espacio.nivel.nombre} "
        f"del proyecto {instance.espacio.nivel.proyecto.nombre}"
    )
    
    # ========================================
    # 1️⃣ ASIGNACIÓN DE ACTIVIDAD
    # ========================================
    if instance.asignado and (created or (asignado_anterior is None and instance.asignado is not None)):
        print(f" ✅ CASO 1: Asignación de actividad")
        
        link_rel = reverse('modificar_actividad', args=[instance.id])
        link = f"https://{settings.ALLOWED_HOSTS[0]}{link_rel}" if settings.ALLOWED_HOSTS else link_rel
        
        mensaje = (
            f"Se te ha asignado la actividad '{instance.nombre}' "
            f"en el espacio {instance.espacio.nombre} "
            f"del nivel {instance.espacio.nivel.nombre} "
            f"del proyecto {instance.espacio.nivel.proyecto.nombre}"
        )
        
        Notificacion.objects.create(
            usuario=instance.asignado,
            mensaje=mensaje,
            actividad=instance,
            link=link
        )
        print(f" ✅ Notificación de asignación creada en BD")
        
        token = getattr(instance.asignado, 'fcm_token', None)
        if token:
            print(f" 📤 Enviando push a {instance.asignado.email}...")
            enviar_notificacion_push(
                "Nueva Actividad Asignada", 
                mensaje, 
                token, 
                usuario=instance.asignado,  # ✅ AGREGAR
                url=link
            )
        else:
            print(f" ⚠️ {instance.asignado.email} no tiene token FCM")

    # ========================================
    # 2️⃣ ACTIVIDAD PASA A "POR ASIGNAR"
    # ========================================
    if (not created and 
        asignacion_anterior != 'por_asignar' and 
        instance.estado_asignacion == 'por_asignar'):
        
        print(f" ✅ CASO 2: Actividad cambió a POR ASIGNAR")
        
        empresa = getattr(instance.asignado, 'empresa', None) if instance.asignado else None
        
        if empresa:
            mensaje = (
                f"La actividad '{instance.nombre}' "
                f"del espacio {instance.espacio.nombre} "
                f"del nivel {instance.espacio.nivel.nombre} "
                f"del proyecto {instance.espacio.nivel.proyecto.nombre} "
                f"está POR ASIGNAR y requiere atención"
            )
            
            usuarios_admin = Usuario.objects.filter(
                tipo_usuario__in=['admin_empresa', 'superadmin_empresa'],
                empresa=empresa
            )
            
            print(f" 👥 Administradores a notificar: {usuarios_admin.count()}")
            
            for usuario in usuarios_admin:
                Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                token = getattr(usuario, 'fcm_token', None)
                if token:
                    print(f" 📤 Enviando push a {usuario.email}...")
                    enviar_notificacion_push(
                        "⚠️ Actividad por Asignar", 
                        mensaje, 
                        token,
                        usuario=usuario  # ✅ AGREGAR
                    )

    # ========================================
    # 3️⃣ ACTIVIDAD EJECUTADA AL 100% CON APROBACIÓN
    # ========================================
    if (not created and 
        instance.avance == 100 and
        estado_anterior != 'ejecutada' and 
        instance.estado_ejecucion == 'ejecutada' and
        instance.aprobacion_calidad == True and
        estado_anterior != 'observada'):
        
        print(f" ✅ CASO 3: Actividad EJECUTADA al 100% (con aprobación calidad)")
        
        mensaje = (
            f"{instance.asignado.get_full_name() or instance.asignado.email} "
            f"completó {detalle_actividad}, "
            f"a la espera de revisión"
        )
        
        usuarios_calidad = Usuario.objects.filter(tipo_usuario='calidad', empresa=empresa_asignado)
        
        print(f" 👥 Usuarios calidad encontrados: {usuarios_calidad.count()}")
        
        for usuario in usuarios_calidad:
            Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
            token = getattr(usuario, 'fcm_token', None)
            if token:
                print(f" 📤 Enviando push a {usuario.email}...")
                enviar_notificacion_push(
                    "Actividad Completada", 
                    mensaje, 
                    token,
                    usuario=usuario  # ✅ AGREGAR
                )

        # ========================================
        # 4️⃣ ACTIVIDAD EJECUTADA AL 100% SIN APROBACIÓN
        # ========================================
        if (not created and 
            instance.avance == 100 and
            estado_anterior != 'ejecutada' and 
            instance.estado_ejecucion == 'ejecutada' and
            instance.aprobacion_calidad == False and
            estado_anterior != 'observada'):
            
            print(f" ✅ CASO 4: Actividad EJECUTADA al 100% (sin aprobación calidad)")
            
            mensaje = (
                f"{instance.asignado.get_full_name() or instance.asignado.email} "
                f"completó {detalle_actividad}, "
                f"pendiente de aprobación"
            )
            
            usuarios_admin = Usuario.objects.filter(tipo_usuario='admin_empresa', empresa=empresa_asignado)
            
            print(f" 👥 Usuarios admin encontrados: {usuarios_admin.count()}")
            
            for usuario in usuarios_admin:
                Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                token = getattr(usuario, 'fcm_token', None)
                if token:
                    print(f" 📤 Enviando push a {usuario.email}...")
                    enviar_notificacion_push(
                        "Actividad Completada", 
                        mensaje, 
                        token,
                        usuario=usuario  # ✅ AGREGAR
                    )

        # ========================================
        # 5️⃣ ACTIVIDAD OBSERVADA
        # ========================================
        if (not created and 
            estado_anterior != 'observada' and 
            instance.estado_ejecucion == 'observada'):
            
            print(f" ✅ CASO 5: Actividad marcada como OBSERVADA")
            
            mensaje = (
                f"La actividad '{instance.nombre}' "
                f"del espacio {instance.espacio.nombre} "
                f"del nivel {instance.espacio.nivel.nombre} "
                f"del proyecto {instance.espacio.nivel.proyecto.nombre} "
                f"fue marcada como OBSERVADA. "
                f"Realiza las correcciones necesarias"
            )
            
            Notificacion.objects.create(usuario=instance.asignado, mensaje=mensaje, actividad=instance)
            print(f" ✅ Notificación de OBSERVADA creada para {instance.asignado.email}")
            
            token = getattr(instance.asignado, 'fcm_token', None)
            if token:
                print(f" 📤 Enviando push a {instance.asignado.email}...")
                enviar_notificacion_push(
                    "⚠️ Actividad Observada", 
                    mensaje, 
                    token,
                    usuario=instance.asignado  # ✅ AGREGAR
                )

        # ========================================
        # 6️⃣ CORRECCIÓN: OBSERVADA → EJECUTADA
        # ========================================
        if (not created and 
            estado_anterior == 'observada' and 
            instance.estado_ejecucion == 'ejecutada' and
            (instance.justificacion or instance.archivo_justificacion)):
            
            print(f" ✅ CASO 6: Actividad CORREGIDA (observada → ejecutada) con justificación")
            
            if instance.aprobacion_calidad == True:
                mensaje = (
                    f"El supervisor {instance.asignado.get_full_name() or instance.asignado.email} "
                    f"corrigió {detalle_actividad}, "
                    f"a la espera de revisión"
                )
                
                usuarios_calidad = Usuario.objects.filter(tipo_usuario='calidad', empresa=empresa_asignado)
                
                print(f" 👥 Usuarios calidad encontrados: {usuarios_calidad.count()}")
                
                for usuario in usuarios_calidad:
                    Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                    token = getattr(usuario, 'fcm_token', None)
                    if token:
                        print(f" 📤 Enviando push a {usuario.email}...")
                        enviar_notificacion_push(
                            "Actividad Corregida", 
                            mensaje, 
                            token,
                            usuario=usuario  # ✅ AGREGAR
                        )
            else:
                mensaje = (
                    f"El supervisor {instance.asignado.get_full_name() or instance.asignado.email} "
                    f"corrigió {detalle_actividad}"
                )
                
                usuarios_admin = Usuario.objects.filter(tipo_usuario='admin_empresa', empresa=empresa_asignado)
                
                print(f" 👥 Usuarios admin encontrados: {usuarios_admin.count()}")
                
                for usuario in usuarios_admin:
                    Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                    token = getattr(usuario, 'fcm_token', None)
                    if token:
                        print(f" 📤 Enviando push a {usuario.email}...")
                        enviar_notificacion_push(
                            "Actividad Corregida", 
                            mensaje, 
                            token,
                            usuario=usuario  # ✅ AGREGAR
                        )

        # ========================================
        # 7️⃣ ACTIVIDAD REVISADA
        # ========================================
        if (not created and 
            estado_anterior != 'revisada' and 
            instance.estado_ejecucion == 'revisada'):
            
            print(f" ✅ CASO 7: Actividad REVISADA")
            
            mensaje = (
                f"La actividad '{instance.nombre}' "
                f"del espacio {instance.espacio.nombre} "
                f"del nivel {instance.espacio.nivel.nombre} "
                f"del proyecto {instance.espacio.nivel.proyecto.nombre} "
                f"ha sido revisada y aprobada correctamente"
            )
            
            usuarios = Usuario.objects.filter(
                tipo_usuario__in=['calidad', 'superadmin_empresa'],
                empresa=empresa_asignado
            )
            
            print(f" 👥 Usuarios a notificar: {usuarios.count()}")
            
            for usuario in usuarios:
                Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                token = getattr(usuario, 'fcm_token', None)
                if token:
                    print(f" 📤 Enviando push a {usuario.email}...")
                    enviar_notificacion_push(
                        "✅ Actividad Revisada", 
                        mensaje, 
                        token,
                        usuario=usuario  # ✅ AGREGAR
                    )