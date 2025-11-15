from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Actividad, Notificacion, Usuario
from django.urls import reverse
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, messaging
import os

# Inicializar Firebase Admin SDK (solo una vez)
if not firebase_admin._apps:
    try:
        cred_path = os.path.join(settings.BASE_DIR, 'credentials', 'firebase-key.json')
        
        if not os.path.exists(cred_path):
            print(f"⚠️ No se encontró el archivo de credenciales en: {cred_path}")
        else:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK inicializado correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar Firebase: {e}")


def enviar_notificacion_push(titulo, mensaje_texto, token, url=None):
    """
    Envía una notificación push usando Firebase Cloud Messaging HTTP v1
    """
    print(f"🔔 INTENTANDO ENVIAR NOTIFICACIÓN")
    print(f"   Título: {titulo}")
    print(f"   Mensaje: {mensaje_texto}")
    print(f"   Token: {token[:30] if token else 'NINGUNO'}...")
    print(f"   URL: {url}")
    print(f"   DEBUG mode: {settings.DEBUG}")
    
    try:
        # Configuración base del webpush
        webpush_config = messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                icon="/static/construccion1app/img/logo2.jpeg",
                badge="/static/construccion1app/img/logo2.jpeg",
                vibrate=[200, 100, 200]
            )
        )
        
        # SOLO agregar link si estamos en producción (NO DEBUG)
        if settings.DEBUG:
            # En desarrollo local, NO enviamos link
            print(f"   ℹ️ Modo desarrollo: Link omitido para evitar error HTTPS")
        else:
            # En producción con HTTPS, SÍ enviamos link
            if url:
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
#  GUARDAR ASIGNACIÓN ANTERIOR
# -----------------------------
@receiver(pre_save, sender=Actividad)
def guardar_asignado_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = Actividad.objects.get(pk=instance.pk)
            instance._asignado_anterior = anterior.asignado
        except Actividad.DoesNotExist:
            instance._asignado_anterior = None
    else:
        instance._asignado_anterior = None


# -----------------------------
#  ACTIVIDAD ASIGNADA
# -----------------------------
@receiver(post_save, sender=Actividad)
def crear_notificacion_asignacion(sender, instance, created, **kwargs):
    """
    Notifica cuando se asigna una actividad a un usuario
    """
    print(f"\n{'='*60}")
    print(f"🔔 SIGNAL: crear_notificacion_asignacion")
    print(f"   Created: {created}")
    print(f"   Actividad: {instance.nombre}")
    print(f"   Asignado: {instance.asignado}")
    print(f"   Asignado anterior: {getattr(instance, '_asignado_anterior', None)}")
    
    # Caso 1: Actividad recién creada con asignado
    if created and instance.asignado:
        print(f"   ✅ Caso 1: Actividad nueva con asignado")
        link = reverse('modificar_actividad', args=[instance.id])
        mensaje = f"Se te ha asignado la actividad: {instance.nombre} en el espacio {instance.espacio.nombre} del nivel {instance.espacio.nivel.nombre} del proyecto {instance.espacio.nivel.proyecto.nombre}"

        # Crear notificación en BD
        Notificacion.objects.create(
            usuario=instance.asignado,
            mensaje=mensaje,
            actividad=instance,
            link=link
        )
        print(f"   ✅ Notificación creada en BD")

        # Enviar push
        token = getattr(instance.asignado, 'fcm_token', None)
        if token:
            print(f"   📤 Enviando push a {instance.asignado.email}...")
            enviar_notificacion_push("Nueva Actividad Asignada", mensaje, token, link)
        else:
            print(f"   ⚠️ {instance.asignado.email} no tiene token FCM registrado.")

    # Caso 2: Actividad existente se le asigna usuario por primera vez
    elif not created:
        asignado_anterior = getattr(instance, '_asignado_anterior', None)
        if asignado_anterior is None and instance.asignado is not None:
            print(f"   ✅ Caso 2: Actividad existente ahora tiene asignado")
            link = reverse('modificar_actividad', args=[instance.id])
            mensaje = f"Se te ha asignado la actividad: {instance.nombre} en el espacio {instance.espacio.nombre} del nivel {instance.espacio.nivel.nombre} del proyecto {instance.espacio.nivel.proyecto.nombre}"

            # Crear notificación en BD
            Notificacion.objects.create(
                usuario=instance.asignado,
                mensaje=mensaje,
                actividad=instance,
                link=link
            )
            print(f"   ✅ Notificación creada en BD")

            # Enviar push
            token = getattr(instance.asignado, 'fcm_token', None)
            if token:
                print(f"   📤 Enviando push a {instance.asignado.email}...")
                enviar_notificacion_push("Nueva Actividad Asignada", mensaje, token, link)
            else:
                print(f"   ⚠️ {instance.asignado.email} no tiene token FCM registrado.")
        else:
            print(f"   ℹ️ No se cumple condición para notificar asignación")
    
    print(f"{'='*60}\n")


# -----------------------------
#  ACTUALIZACIONES Y ESTADOS
# -----------------------------
@receiver(pre_save, sender=Actividad)
def actividad_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        instance._pre_save_avance = None
        instance._pre_save_estado = None
    else:
        try:
            old = Actividad.objects.get(pk=instance.pk)
            instance._pre_save_avance = old.avance
            instance._pre_save_estado = old.estado_ejecucion
        except Actividad.DoesNotExist:
            instance._pre_save_avance = None
            instance._pre_save_estado = None


@receiver(post_save, sender=Actividad)
def actividad_post_save_notificaciones(sender, instance, created, **kwargs):
    """
    Notifica cambios de avance y estado de actividades
    """
    pre_avance = getattr(instance, '_pre_save_avance', None)
    pre_estado = getattr(instance, '_pre_save_estado', None)

    print(f"\n{'='*60}")
    print(f"🔔 SIGNAL: actividad_post_save_notificaciones")
    print(f"   Actividad: {instance.nombre}")
    print(f"   Created: {created}")
    print(f"   Avance anterior: {pre_avance} → Actual: {instance.avance}")
    print(f"   Estado anterior: {pre_estado} → Actual: {instance.estado_ejecucion}")
    print(f"   Asignado: {instance.asignado}")

    if not instance.asignado:
        print(f"   ⚠️ No hay usuario asignado, omitiendo notificaciones")
        print(f"{'='*60}\n")
        return

    empresa_asignado = getattr(instance.asignado, 'empresa', None)

    # 1️⃣ Avance -> 100 y con aprobación de calidad
    if (not created) and (instance.avance == 100) and instance.aprobacion_calidad == True:
        print(f"   ✅ Caso 1: Avance 100% CON aprobación calidad")
        mensaje = f"{instance.asignado} completó la actividad '{instance.nombre}', a la espera de revisión."
        usuarios_calidad = Usuario.objects.filter(tipo_usuario='calidad', empresa=empresa_asignado)
        print(f"   👥 Usuarios calidad encontrados: {usuarios_calidad.count()}")
        
        for usuario in usuarios_calidad:
            Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
            token = getattr(usuario, 'fcm_token', None)
            if token:
                print(f"   📤 Enviando push a {usuario.email}...")
                enviar_notificacion_push("Actividad Completada", mensaje, token)
            else:
                print(f"   ⚠️ {usuario.email} no tiene token FCM")

    # 2️⃣ Avance -> 100 sin aprobación de calidad
    if (not created) and (instance.avance == 100) and instance.aprobacion_calidad == False:
        print(f"   ✅ Caso 2: Avance 100% SIN aprobación calidad")
        mensaje = f"{instance.asignado} completó la actividad '{instance.nombre}', pendiente de aprobación."
        usuarios_admin = Usuario.objects.filter(tipo_usuario='admin_empresa', empresa=empresa_asignado)
        print(f"   👥 Usuarios admin encontrados: {usuarios_admin.count()}")
        
        for usuario in usuarios_admin:
            Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
            token = getattr(usuario, 'fcm_token', None)
            if token:
                print(f"   📤 Enviando push a {usuario.email}...")
                enviar_notificacion_push("Actividad Completada", mensaje, token)
            else:
                print(f"   ⚠️ {usuario.email} no tiene token FCM")

    # 3️⃣ Estado: observada → ejecutada
    if (not created) and (pre_estado == 'observada') and (instance.estado_ejecucion == 'ejecutada') and instance.aprobacion_calidad == True:
        print(f"   ✅ Caso 3: Estado cambió de observada a ejecutada")
        mensaje = f"El supervisor corrigió la actividad '{instance.nombre}', a la espera de revisión."
        usuarios_calidad = Usuario.objects.filter(tipo_usuario='calidad', empresa=empresa_asignado)
        print(f"   👥 Usuarios calidad encontrados: {usuarios_calidad.count()}")
        
        for usuario in usuarios_calidad:
            Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
            token = getattr(usuario, 'fcm_token', None)
            if token:
                print(f"   📤 Enviando push a {usuario.email}...")
                enviar_notificacion_push("Actividad Corregida", mensaje, token)
            else:
                print(f"   ⚠️ {usuario.email} no tiene token FCM")

    print(f"{'='*60}\n")


# -----------------------------
#  OBSERVADA Y REVISADA
# -----------------------------
@receiver(post_save, sender=Actividad)
def notificar_asignado_observada(sender, instance, created, **kwargs):
    """
    Notifica al asignado cuando una actividad es marcada como observada
    """
    if not created and instance.estado_ejecucion == 'observada' and instance.asignado:
        print(f"\n{'='*60}")
        print(f"🔔 SIGNAL: notificar_asignado_observada")
        print(f"   Actividad: {instance.nombre}")
        print(f"   Asignado: {instance.asignado.email}")
        
        mensaje = f"La actividad '{instance.nombre}' fue marcada como OBSERVADA. Revisa los comentarios."
        Notificacion.objects.create(usuario=instance.asignado, mensaje=mensaje, actividad=instance)
        print(f"   ✅ Notificación creada en BD")
        
        token = getattr(instance.asignado, 'fcm_token', None)
        if token:
            print(f"   📤 Enviando push...")
            enviar_notificacion_push("⚠️ Actividad Observada", mensaje, token)
        else:
            print(f"   ⚠️ Usuario no tiene token FCM")
        
        print(f"{'='*60}\n")


@receiver(post_save, sender=Actividad)
def notificar_revision_actividad(sender, instance, created, **kwargs):
    """
    Notifica cuando una actividad es revisada
    """
    if not created and instance.estado_ejecucion == 'revisada' and instance.asignado:
        print(f"\n{'='*60}")
        print(f"🔔 SIGNAL: notificar_revision_actividad")
        print(f"   Actividad: {instance.nombre}")
        print(f"   Asignado: {instance.asignado.email}")
        
        usuarios = Usuario.objects.filter(
            tipo_usuario__in=['calidad', 'superadmin_empresa'], 
            empresa=instance.asignado.empresa
        )
        print(f"   👥 Usuarios a notificar: {usuarios.count()}")
        
        mensaje = f"La actividad '{instance.nombre}' ha sido revisada correctamente."
        
        for usuario in usuarios:
            Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
            token = getattr(usuario, 'fcm_token', None)
            if token:
                print(f"   📤 Enviando push a {usuario.email}...")
                enviar_notificacion_push("✅ Actividad Revisada", mensaje, token)
            else:
                print(f"   ⚠️ {usuario.email} no tiene token FCM")
        
        print(f"{'='*60}\n")