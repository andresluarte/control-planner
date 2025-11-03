from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Actividad, Notificacion, Usuario
from django.urls import reverse
from webpush import send_user_notification
import json

@receiver(pre_save, sender=Actividad)
def guardar_asignado_anterior(sender, instance, **kwargs):
    if instance.pk:
        anterior = Actividad.objects.get(pk=instance.pk)
        instance._asignado_anterior = anterior.asignado
    else:
        instance._asignado_anterior = None


@receiver(post_save, sender=Actividad)
def crear_notificacion_asignacion(sender, instance, created, **kwargs):
    if created and instance.asignado:
        link = reverse('modificar_actividad', args=[instance.id])
        mensaje = f"Se te ha asignado la actividad: {instance.nombre} en el espacio {instance.espacio.nombre} del nivel {instance.espacio.nivel.nombre} del proyecto {instance.espacio.nivel.proyecto.nombre}"
        
        # Crear notificación en BD
        Notificacion.objects.create(
            usuario=instance.asignado,
            mensaje=mensaje,
            actividad=instance,
            link=link
        )
        
        # Enviar notificación push
        payload = {
            "head": "Nueva Actividad Asignada",
            "body": mensaje,
            "url": link
        }
        try:
            send_user_notification(
                user=instance.asignado,
                payload=payload,
                ttl=1000
            )
            print(f"✅ Push enviado a {instance.asignado}")
        except Exception as e:
            print(f"❌ Error enviando push: {e}")
            
    else:
        # Caso: actualización -> verificar si antes no había asignado y ahora sí
        if instance._asignado_anterior is None and instance.asignado is not None:
            link = reverse('modificar_actividad', args=[instance.id])
            mensaje = f"Se te ha asignado la actividad: {instance.nombre} en el espacio {instance.espacio.nombre} del nivel {instance.espacio.nivel.nombre} del proyecto {instance.espacio.nivel.proyecto.nombre}"
            
            Notificacion.objects.create(
                usuario=instance.asignado,
                mensaje=mensaje,
                actividad=instance,
                link=link
            )
            
            # Enviar push
            payload = {
                "head": "Nueva Actividad Asignada",
                "body": mensaje,
                "url": link
            }
            try:
                send_user_notification(user=instance.asignado, payload=payload, ttl=1000)
            except Exception as e:
                print(f"❌ Error: {e}")


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
    pre_avance = getattr(instance, '_pre_save_avance', None)
    pre_estado = getattr(instance, '_pre_save_estado', None)

    if not instance.asignado:
        return

    empresa_asignado = getattr(instance.asignado, 'empresa', None)

    # 1) Avance -> 100 con aprobación de calidad
    if (not created) and (instance.avance == 100) and instance.aprobacion_calidad == True:
        mensaje = f"{instance.asignado} ejecutó la actividad: {instance.nombre}, a la espera de revisión"
        usuarios_calidad = Usuario.objects.filter(tipo_usuario='calidad', empresa=empresa_asignado)
        
        for usuario in usuarios_calidad:
            if not Notificacion.objects.filter(usuario=usuario, actividad=instance, mensaje=mensaje).exists():
                Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                
                # Enviar push
                payload = {
                    "head": "Actividad Completada",
                    "body": mensaje,
                    "url": reverse('modificar_actividad', args=[instance.id])
                }
                try:
                    send_user_notification(user=usuario, payload=payload, ttl=1000)
                    print(f"✅ Push enviado a calidad ({usuario})")
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    # 2) Avance -> 100 sin aprobación de calidad
    if (not created) and (instance.avance == 100) and instance.aprobacion_calidad == False:
        mensaje = f"{instance.asignado} ejecutó la actividad: {instance.nombre}, a la espera de revisión"
        usuarios_admin_empresa = Usuario.objects.filter(tipo_usuario='admin_empresa', empresa=empresa_asignado)
        
        for usuario in usuarios_admin_empresa:
            if not Notificacion.objects.filter(usuario=usuario, actividad=instance, mensaje=mensaje).exists():
                Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                
                # Enviar push
                payload = {
                    "head": "Actividad Completada",
                    "body": mensaje,
                    "url": reverse('modificar_actividad', args=[instance.id])
                }
                try:
                    send_user_notification(user=usuario, payload=payload, ttl=1000)
                    print(f"✅ Push enviado a Admin ({usuario})")
                except Exception as e:
                    print(f"❌ Error: {e}")

    # 3) Estado: observada -> ejecutada
    if (not created) and (pre_estado == 'observada') and (instance.estado_ejecucion == 'ejecutada') and instance.aprobacion_calidad == True:
        mensaje = f"El supervisor corrigió la actividad '{instance.nombre}', a la espera de revisión"
        usuarios_calidad = Usuario.objects.filter(tipo_usuario='calidad', empresa=empresa_asignado)
        
        for usuario in usuarios_calidad:
            if not Notificacion.objects.filter(usuario=usuario, actividad=instance, mensaje=mensaje).exists():
                Notificacion.objects.create(usuario=usuario, mensaje=mensaje, actividad=instance)
                
                # Enviar push
                payload = {
                    "head": "Actividad Corregida",
                    "body": mensaje,
                    "url": reverse('modificar_actividad', args=[instance.id])
                }
                try:
                    send_user_notification(user=usuario, payload=payload, ttl=1000)
                    print(f"✅ Push enviado a calidad ({usuario})")
                except Exception as e:
                    print(f"❌ Error: {e}")


@receiver(post_save, sender=Actividad)
def notificar_asignado_observada(sender, instance, created, **kwargs):
    if not created and instance.estado_ejecucion == 'observada' and instance.asignado:
        mensaje = f"La actividad '{instance.nombre}' fue marcada como OBSERVADA por calidad. Requiere tu revisión."
        
        Notificacion.objects.create(
            usuario=instance.asignado,
            mensaje=mensaje,
            actividad=instance
        )
        
        # Enviar push
        payload = {
            "head": "⚠️ Actividad Observada",
            "body": mensaje,
            "url": reverse('modificar_actividad', args=[instance.id])
        }
        try:
            send_user_notification(user=instance.asignado, payload=payload, ttl=1000)
            print(f"✅ Push enviado a {instance.asignado}")
        except Exception as e:
            print(f"❌ Error: {e}")


@receiver(post_save, sender=Actividad)
def notificar_revision_actividad(sender, instance, created, **kwargs):
    if not created and instance.estado_ejecucion == 'revisada' and instance.asignado:
        usuarios_calidad = Usuario.objects.filter(
            tipo_usuario='calidad',
            empresa=instance.asignado.empresa
        )

        admin_empresa = Usuario.objects.filter(
            tipo_usuario='superadmin_empresa',
            empresa=instance.asignado.empresa
        )

        destinatarios = list(usuarios_calidad) + list(admin_empresa)
        mensaje = f"La actividad '{instance.nombre}' ha sido revisada."

        for usuario in destinatarios:
            Notificacion.objects.create(
                usuario=usuario,
                mensaje=mensaje,
                actividad=instance
            )
            
            # Enviar push
            payload = {
                "head": "✅ Actividad Revisada",
                "body": mensaje,
                "url": reverse('modificar_actividad', args=[instance.id])
            }
            try:
                send_user_notification(user=usuario, payload=payload, ttl=1000)
                print(f"✅ Push enviado a {usuario}")
            except Exception as e:
                print(f"❌ Error: {e}")