from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Proyecto,Empresa
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import AgregarUsuarioForm,LoginForm

# Create your views here.
def home(request):
    return render(request, 'construccion1app/home.html')


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Proyecto

class MisProyectosViewHome(LoginRequiredMixin, ListView):
    template_name = 'construccion1app/mis_proyectosHome.html'
    context_object_name = 'proyectos'

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            # Superusuario ve todos los proyectos
            return Proyecto.objects.all()

        if user.tipo_usuario in ['superadmin_empresa', 'admin_empresa'] and user.empresa:
            # Administradores de empresa ven todos los proyectos de su empresa
            return Proyecto.objects.filter(empresa=user.empresa)

        if user.empresa:
            # Usuarios normales solo ven proyectos a los que tienen acceso
            return Proyecto.objects.filter(
                empresa=user.empresa,
                usuarios_acceso=user
            )

        # Si no tiene empresa ni proyectos asignados
        return Proyecto.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar datos procesados de cada proyecto
        proyectos_con_datos = []
        for proyecto in context['proyectos']:
            # Calcular el avance total del proyecto
            avance_total = proyecto.calcular_avance()
            
            # Crear un diccionario con los datos del proyecto
            proyecto_data = {
                'id': proyecto.id,
                'nombre': proyecto.nombre,
                'rubro': proyecto.rubro,
                'ubicacion': proyecto.ubicacion,
                'descripcion': proyecto.descripcion,
                'fecha_inicio': proyecto.fecha_inicio,
                'fecha_fin': proyecto.fecha_fin,
                'avance_total': float(avance_total),  # Asegurar que sea float
            }
            proyectos_con_datos.append(proyecto_data)
        
        # Reemplazar proyectos con los datos procesados
        context['proyectos_data'] = proyectos_con_datos
        
        return context


@login_required
def editar_visibilidad(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    # Solo superadmin_empresa o admin_empresa pueden acceder
    if not request.user.tipo_usuario in ['superadmin_empresa', 'admin_empresa']:
        return redirect('mis_proyectosHome')  # O mostrar un mensaje de error

    # Obtenemos los usuarios de tipo supervisor_constructor o calidad
    usuarios = Usuario.objects.filter(tipo_usuario__in=['supervisor_constructor', 'calidad'], empresa=request.user.empresa)
    
    if request.method == 'POST':
        seleccionados_ids = request.POST.getlist('usuarios')
        proyecto.usuarios_acceso.set(seleccionados_ids)
        return redirect('mis_proyectos')

    context = {
        'proyecto': proyecto,
        'usuarios': usuarios,
    }
    return render(request, 'construccion1app/editar_visibilidad.html', context)

    
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('mis_proyectos')  # Cambia 'home' por tu URL de inicio
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = LoginForm()
    return render(request, 'construccion1app/login.html', {"form" :form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# construccion1app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario

# views.py
@login_required
def agregarusuario(request):
    # Solo SuperAdministrador de Empresa y Administrador de Empresa
    if request.user.tipo_usuario not in ['superadmin_empresa', 'admin_empresa']:
        messages.error(request, "No tienes permisos para agregar usuarios.")
        return redirect('mis_proyectos')

    if request.method == "POST":
        form = AgregarUsuarioForm(request.POST, creador=request.user)
        if form.is_valid():
            nuevo_usuario = form.save(commit=False)
            nuevo_usuario.empresa = request.user.empresa  # Empresa automática
            nuevo_usuario.save()
            messages.success(request, f"Usuario {nuevo_usuario.username} creado correctamente.")
            return redirect('mis_proyectos')
    else:
        form = AgregarUsuarioForm(creador=request.user)

    return render(request, 'construccion1app/agregar_usuario.html', {'form': form})

@login_required
def lista_usuarios_empresa(request):
    # Solo SuperAdminEmpresa y AdminEmpresa pueden acceder
    if request.user.tipo_usuario not in ["superadmin_empresa", "admin_empresa"]:
        messages.error(request, "No tienes permisos para ver esta lista.")
        return redirect('mis_proyectos')

    # Filtrar usuarios de la misma empresa
    usuarios = Usuario.objects.filter(empresa=request.user.empresa)

    return render(request, 'construccion1app/lista_usuarios.html', {'usuarios': usuarios})


@login_required
def lista_empresas(request):
    # Superusuario no puede acceder
   

    # Mostrar solo la empresa a la que pertenece el usuario
    if request.user.empresa:
        empresas = Empresa.objects.filter(id=request.user.empresa.id)
    else:
        empresas = Empresa.objects.none()  # No tiene empresa

    return render(request, 'construccion1app/lista_empresas.html', {'empresas': empresas})



@login_required
def mi_perfil(request):
    # Bloqueo para superuser


    usuario = request.user  # Usuario logueado
    empresa = getattr(usuario, 'empresa', None)  # Solo si tiene empresa asignada

    context = {
        'usuario': usuario,
        'empresa': empresa,
    }
    return render(request, 'construccion1app/miperfil.html', context)


from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from decimal import Decimal, ROUND_HALF_UP

@login_required
def dashboard_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    # Validar si el usuario puede ver el formulario
    mostrar_formulario = request.user.tipo_usuario in ["superadmin_empresa", "admin_empresa"]

    # Manejo del formulario
    if mostrar_formulario and request.method == "POST":
        form = NivelForm(request.POST)
        if form.is_valid():
            nivel = form.save(commit=False)
            nivel.proyecto = proyecto
            nivel.save()
            form = NivelForm()  # limpiar formulario después de guardar
    else:
        form = NivelForm() if mostrar_formulario else None

    # Construcción de datos de niveles y espacios
    datos_niveles = []
    for nivel in proyecto.niveles.all():
        datos_espacios = []
        for espacio in nivel.espacios.all():
            actividades = [
                {
                    "id": a.id,
                    "nombre": a.nombre,
                    "avance": a.avance,
                    "incidencia": a.incidencia,
                    "ponderado": a.calcular_avance_ponderado(),
                    "asignado": a.asignado,
                    "estado_ejecucion": a.get_estado_ejecucion_display(),
                    "habilitada": a.habilitada,
                    "predecesora": a.predecesora.nombre if a.predecesora else None,
                    "sucesora": a.sucesora.nombre if a.sucesora else None,               
                    "fecha_inicio": a.fecha_inicio,
                    "fecha_fin": a.fecha_fin,
                    "estado_asignacion": a.estado_asignacion,
                    "archivo_informacion": a.archivo_informacion,  # <-- aquí

                    
                }
                for a in espacio.actividades.all().order_by('id')  # <-- aquí
            ]

            # 👉 calcular incidencias de actividades de este espacio
            total_incidencia = espacio.actividades.aggregate(total=Sum("incidencia"))["total"] or 0
            total_incidencia = float(round(total_incidencia, 2))
            print(f"Espacio '{espacio.nombre}' tiene total de incidencias: {total_incidencia}")

            datos_espacios.append({
                "id": espacio.id,
                "nombre": espacio.nombre,
                "avance": sum(a["ponderado"] for a in actividades),
                "incidencia": espacio.incidencia,
                "ponderado": espacio.calcular_avance_ponderado(),
                "total_incidencia": total_incidencia,  # 👈 cada espacio tiene su propio total
                "actividades": actividades,
            })

        datos_niveles.append({
            "id": nivel.id,
            "nombre": nivel.nombre,
            "avance": sum(e["ponderado"] for e in datos_espacios),
            "incidencia": nivel.incidencia,
            "ponderado": nivel.calcular_avance_ponderado(),
            "espacios": datos_espacios,
        })

    avance_total = proyecto.calcular_avance()

    # Renderizar el dashboard con formulario y niveles
    # ❌ QUITA esta línea porque ya no necesitas pasar total_incidencia global
    return render(request, "construccion1app/dashboard_proyecto.html", {
        "proyecto": proyecto,
        "niveles": datos_niveles,
        "avance_total": avance_total,
        "form": form,
        "mostrar_formulario": mostrar_formulario,
        # ❌ NO pases "total_incidencia" aquí
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Proyecto,Nivel,Espacio,Actividad
from .forms import ProyectoForm,NivelForm,EspacioForm,ActividadForm,ModificarActividadForm

@login_required
def agregar_proyecto(request):
    # Validar tipo de usuario
    if request.user.tipo_usuario not in ["superadmin_empresa", "admin_empresa"]:
        raise PermissionDenied("No tienes permiso para crear proyectos.")

    if request.method == "POST":
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.empresa = request.user.empresa  # Se asigna automáticamente
            proyecto.save()
            return redirect('mis_proyectos')  # Nombre de la vista donde listamos proyectos
    else:
        form = ProyectoForm()
    
    return render(request, "construccion1app/agregar_proyecto.html", {"form": form})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Proyecto
@login_required
def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    # Restringir acceso SOLO a superusuario y superadmin_empresa
    if not (request.user.tipo_usuario in ['superusuario', 'superadmin_empresa']):
        return HttpResponseForbidden("No tienes permisos para eliminar proyectos.")

    if request.method == "POST":
        proyecto.delete()
        messages.success(request, "✅ Proyecto eliminado correctamente")
        return redirect("mis_proyectos")  # Ajusta la redirección según tu app

    return redirect('dashboard_proyecto', proyecto_id=proyecto.id)



@login_required
def eliminar_nivel(request, pk):
    nivel = get_object_or_404(Nivel, pk=pk)

    if not (request.user.tipo_usuario in ['superusuario', 'superadmin_empresa']):
        return HttpResponseForbidden("No tienes permisos para eliminar el Nivel.")

    if request.method == "POST":
        nivel.delete()
        messages.success(request, "✅ Nivel eliminado correctamente")
        return redirect('dashboard_proyecto', proyecto_id=nivel.proyecto.id)

    return redirect('dashboard_proyecto', proyecto_id=nivel.proyecto.id)



@login_required
def agregar_nivel(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    # Validar tipo de usuario
    if request.user.tipo_usuario not in ["superadmin_empresa", "admin_empresa"]:
        raise PermissionDenied("No tienes permiso para crear niveles.")

    if request.method == "POST":
        form = NivelForm(request.POST)
        if form.is_valid():
            nivel = form.save(commit=False)
            nivel.proyecto = proyecto  # <-- asignar al proyecto correcto
            nivel.save()
            return redirect('dashboard_proyecto', proyecto_id=proyecto.id)
        else:
            # Si el formulario no es válido, volver a renderizar la plantilla con errores
            return render(request, "construccion1app/dashboard_proyecto.html", {"form": form, "proyecto": proyecto})
    else:
        form = NivelForm()
        return render(request, "construccion1app/dashboard_proyecto.html", {"form": form, "proyecto": proyecto})
    

from django.http import JsonResponse

def sumar_incidencias(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    suma = Nivel.objects.filter(proyecto=proyecto).aggregate(total=Sum("incidencia"))["total"] or 0
    return JsonResponse({"suma": suma})



from django.db.models import Sum

@login_required
def agregar_espacio(request, nivel_id):
    nivel = get_object_or_404(Nivel, id=nivel_id)
    total_actual = nivel.espacios.aggregate(total=Sum('incidencia'))['total'] or 0


    if request.method == "POST":
        form = EspacioForm(request.POST, nivel=nivel)
        if form.is_valid():
            espacio = form.save(commit=False)
            espacio.nivel = nivel
            espacio.save()
            messages.success(request, "Espacio agregado con éxito.")
            return redirect('dashboard_proyecto', proyecto_id=espacio.nivel.proyecto.id)
    else:
        form = EspacioForm(nivel=nivel)

    return render(request, 'construccion1app/agregar_espacio.html', {
        'form': form,
        'nivel': nivel,
        'total_actual': total_actual,  # 👉 aquí pasamos el total al template
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Espacio

def eliminar_espacio(request, pk):
    espacio = get_object_or_404(Espacio, pk=pk)

    if not (request.user.is_superuser or request.user.tipo_usuario == 'superadmin_empresa'):
        return HttpResponseForbidden("No tienes permisos para eliminar espacios.")

    if request.method == "POST":
        proyecto_id = espacio.nivel.proyecto.id  # para redirigir al detalle del proyecto
        espacio.delete()
        messages.success(request, "✅ Espacio eliminado correctamente")
        return redirect('dashboard_proyecto', proyecto_id=espacio.nivel.proyecto.id)

    return redirect('dashboard_proyecto', proyecto_id=espacio.nivel.proyecto.id)


@login_required 
def agregar_actividad(request, espacio_id):     
    espacio = get_object_or_404(Espacio, id=espacio_id)      
    
    # Validar tipo de usuario     
    if request.user.tipo_usuario not in ['superadmin_empresa', 'admin_empresa', 'superuser']:         
        raise PermissionDenied("No tienes permiso para crear una actividad")      
    
    if request.method == "POST":         
        form = ActividadForm(
            request.POST, 
            request.FILES,  # Agregar files para manejar uploads
            user=request.user, 
            espacio=espacio  # Pasar espacio como parámetro
        )
        
        if form.is_valid():             
            # Simplificar el guardado - dejar que el form.save() maneje todo
            actividad = form.save()
            
            # Mostrar mensaje sobre la relación establecida
            if hasattr(form, 'relacion_establecida') and form.relacion_establecida:
                messages.success(request, f'Actividad creada correctamente. {form.relacion_establecida}')
            else:
                messages.success(request, 'Actividad creada correctamente')
                
            return redirect('dashboard_proyecto', proyecto_id=espacio.nivel.proyecto.id)
        
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
            
    else:         
        form = ActividadForm(
            user=request.user, 
            espacio=espacio  # Pasar espacio como parámetro
        )      
    
    return render(request, 'construccion1app/agregar_actividad.html', {
        'form': form, 
        'espacio': espacio,
        'user': request.user,  # Pasar user al template
    })

from django.http import JsonResponse

@login_required
def mapa_actividades(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)
    actividades = Actividad.objects.filter(espacio=espacio)

    # Construir lista de nodos y relaciones
    nodes = []
    edges = []

    for act in actividades:
        nodes.append({
            'id': act.id,
            'label': act.nombre,
            'estado': act.estado_ejecucion,
            'inicio': act.fecha_inicio.isoformat() if act.fecha_inicio else None
        })
        if act.predecesora:
            edges.append({
                'from': act.predecesora.id,
                'to': act.id
            })
        if act.sucesora:
            edges.append({
                'from': act.id,
                'to': act.sucesora.id
            })

    return JsonResponse({'nodes': nodes, 'edges': edges})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.urls import reverse
@login_required
def modificar_actividad(request, actividad_id):

    # Obtener la actividad
    try:
        actividad = Actividad.objects.get(id=actividad_id)
    except Actividad.DoesNotExist:
        messages.error(request, "❌ La actividad que intentas modificar ya no existe.")
        return redirect('dashboard_proyecto', proyecto_id=actividad.espacio.nivel.proyecto.id)
    sucesora_habilitada = None
    
    # Verificar permisos (opcional)
    if not (
        request.user.tipo_usuario in ['superadmin_empresa', 'admin_empresa', 'superuser','calidad']
        or request.user == actividad.asignado  # 👈 Permitir al usuario asignado
    ):
        raise PermissionDenied("No tienes permiso para modificar esta actividad")
    
    if request.method == 'POST':
        # Crear formulario con datos POST y usuario
        form = ModificarActividadForm(
            data=request.POST, 
            files=request.FILES,
            instance=actividad,                     
            user=request.user
        )
        
        if form.is_valid():
            actividad_actualizada = form.save()
            
            # Obtener el nombre de la sucesora habilitada si existe
            if hasattr(form, 'sucesora_habilitada_nombre') and form.sucesora_habilitada_nombre:
                sucesora_habilitada = form.sucesora_habilitada_nombre
            
            # Mostrar mensaje apropiado
            if sucesora_habilitada:
                messages.success(
                    request, 
                    f'Actividad actualizada correctamente. La actividad sucesora "{sucesora_habilitada}" ha sido habilitada.'
                )
            else:
                messages.success(request, 'Actividad actualizada correctamente')
                
            return redirect( f"{reverse('dashboard_proyecto', args=[actividad.espacio.nivel.proyecto.id])}#actividad-{actividad.id}")
        else:
            messages.error(request, 'Por favor corrige los errores del formulario')
    
    else:
        # Crear formulario vacío con usuario
        form = ModificarActividadForm(
            instance=actividad,
            user=request.user
        )
    
    return render(request, 'construccion1app/modificar_actividad.html', {
        'form': form,
        'actividad': actividad,
        'user': request.user,
        'espacio': actividad.espacio,
        'sucesora_habilitada': sucesora_habilitada,  # También pasamos el user al template
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Actividad

def eliminar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)

    # Control de permisos
    if not (
        request.user.is_superuser
        or request.user.tipo_usuario in ["superadmin_empresa", "admin_empresa"]
        or actividad.asignado == request.user
    ):
        return HttpResponseForbidden("No tienes permisos para eliminar esta actividad.")

    if request.method == "POST":
        proyecto_id = actividad.espacio.nivel.proyecto.id

        actividad.delete()
        messages.success(request, "✅ Actividad eliminada correctamente")
        return redirect('dashboard_proyecto', proyecto_id=actividad.espacio.nivel.proyecto.id)


    return redirect('dashboard_proyecto', proyecto_id=actividad.espacio.nivel.proyecto.id)

# context_processors.py
from .models import Notificacion

def notificaciones_context(request):
    if request.user.is_authenticated:
        notificaciones_no_leidas = request.user.notificaciones.filter(leida=False).count()
    else:
        notificaciones_no_leidas = 0
    return {"notificaciones_no_leidas": notificaciones_no_leidas}


def detalle_notificacion(request, pk):
    # Obtener la notificación del usuario
    notif = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    
    # Marcar como leída
    notif.leida = True
    notif.save()
    
    # Redirigir a la edición de la actividad asociada
    if notif.actividad:  # Asegúrate de que la notificación tenga FK a Actividad
        return redirect('modificar_actividad', actividad_id=notif.actividad.pk)
    
    return redirect('lista_notificaciones')  # O a otra página si no hay actividad asociada



from django.shortcuts import render
from .models import Notificacion
from django.contrib.auth.decorators import login_required

@login_required
def lista_notificaciones(request):
    # Solo del usuario logueado
    notificaciones = request.user.notificaciones.all().order_by('-fecha_creacion')
    return render(request, 'construccion1app/lista_notificaciones.html', {'notificaciones': notificaciones})





from django.http import JsonResponse
from django.db.models import Sum
from .models import Actividad

def incidencia_restante(request, espacio_id):
    exclude_id = request.GET.get("exclude_id")
    qs = Actividad.objects.filter(espacio_id=espacio_id)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)

    total_otras = qs.aggregate(total=Sum("incidencia"))["total"] or 0
    return JsonResponse({"total_otras": total_otras})



import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Actividad, Espacio
from decimal import Decimal

def importar_actividades(request, espacio_id):
    espacio = get_object_or_404(Espacio, id=espacio_id)

    if request.method == "POST" and request.FILES.get("archivo_excel"):
        archivo = request.FILES["archivo_excel"]

        try:
            df = pd.read_excel(archivo)

            # Campos obligatorios
            campos_requeridos = [
                "nombre", "avance", "incidencia",
                "estado_ejecucion", "estado_asignacion", "habilitada"
            ]
            for campo in campos_requeridos:
                if campo not in df.columns:
                    raise ValueError(f"Falta la columna obligatoria: {campo}")

            # Validar que no haya nulos o vacíos
            for campo in campos_requeridos:
                if df[campo].isnull().any() or (df[campo].astype(str).str.strip() == "").any():
                    raise ValueError(f"Existen valores vacíos en la columna: {campo}")

            # Validar suma incidencias
            suma_incidencia = df["incidencia"].sum()
            if round(float(suma_incidencia), 2) != 100.00:
                raise ValueError(f"La suma de incidencias debe ser 100. Actualmente es {suma_incidencia}.")

            # Crear actividades
            for index, row in df.iterrows():
                Actividad.objects.create(
                    espacio=espacio,
                    nombre=row["nombre"],
                    avance=row["avance"],
                    incidencia=Decimal(str(row["incidencia"])),
                    estado_ejecucion=row["estado_ejecucion"],
                    estado_asignacion=row["estado_asignacion"],
                    habilitada=bool(row["habilitada"]),
                )

            messages.success(request, "✅ Actividades importadas con éxito")

        except ValueError as ve:
            # Errores de validación (que tú controlas)
            messages.error(request, str(ve))

        except Exception as e:
            # Errores inesperados (ejemplo: archivo corrupto, error de librería, etc.)
            messages.error(request, f"⚠️ Error al procesar el archivo: {str(e)}")

        return redirect("dashboard_proyecto", proyecto_id=espacio.nivel.proyecto.id)

    return render(request, "construccion1app/importar_actividades.html", {"espacio": espacio})




import datetime
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Proyecto, Actividad

@login_required
def programacion_obra(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    vista = request.GET.get("vista", "kanban")  # por defecto 'kanban'

    # === Capturar filtros GET ===
    nombre = request.GET.get("nombre", "")
    asignado_id = request.GET.get("asignado", "")
    estado_ejecucion = request.GET.get("estado_ejecucion", "")
    estado_asignacion = request.GET.get("estado_asignacion", "")
    habilitada = request.GET.get("habilitada", "")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    avance_min = request.GET.get("avance_min", "")
    avance_max = request.GET.get("avance_max", "")
    nivel_id = request.GET.get("nivel", "")

    espacio_nombre = request.GET.get("espacio")

    # === Filtrar actividades ===
    actividades_qs = Actividad.objects.filter(espacio__nivel__proyecto=proyecto)

    if nombre:
        actividades_qs = actividades_qs.filter(nombre__icontains=nombre)
    if asignado_id:
        actividades_qs = actividades_qs.filter(asignado_id=asignado_id)
    if estado_ejecucion:
        actividades_qs = actividades_qs.filter(estado_ejecucion=estado_ejecucion)
    if estado_asignacion:
        actividades_qs = actividades_qs.filter(estado_asignacion=estado_asignacion)
    if habilitada:
        actividades_qs = actividades_qs.filter(habilitada=(habilitada == "true"))
    if fecha_inicio:
        actividades_qs = actividades_qs.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        actividades_qs = actividades_qs.filter(fecha_fin__lte=fecha_fin)
    if avance_min:
        actividades_qs = actividades_qs.filter(avance__gte=avance_min)
    if avance_max:
        actividades_qs = actividades_qs.filter(avance__lte=avance_max)
    if nivel_id:
        actividades_qs = actividades_qs.filter(espacio__nivel_id=nivel_id)
    if espacio_nombre:
        actividades_qs = actividades_qs.filter(espacio__nombre__icontains=espacio_nombre)
    # === Estados ===
    ESTADO_EJECUCION_CHOICES = {
        "no_ejecutada": "No ejecutada",
        "ejecucion": "En ejecución",
        "ejecutada": "Ejecutada",
        "observada": "Observada",
        "revisada": "Revisada",
    }

    estados = {key: [] for key in ESTADO_EJECUCION_CHOICES.keys()}

    for actividad in actividades_qs.select_related("espacio__nivel", "asignado"):
        nivel = actividad.espacio.nivel
        espacio = actividad.espacio
        inicio = actividad.fecha_inicio
        fin = actividad.fecha_fin
        dias = (fin - inicio).days + 1 if inicio and fin else None

        estados[actividad.estado_ejecucion].append({
            "nivel": nivel.nombre,
            "espacio": espacio.nombre,
            "actividad": actividad,
            "asignado": actividad.asignado,
            "dias": dias,
        })

    context = {
        "proyecto": proyecto,
        "estados": estados,
        "ESTADO_EJECUCION_CHOICES": ESTADO_EJECUCION_CHOICES,
        "vista": vista,
        "hoy": date.today(),
        "asignados": proyecto.niveles.first().espacios.first().actividades.model.objects.filter(asignado__isnull=False).values_list("asignado__id", "asignado__username").distinct(),
        # Para mostrar los filtros seleccionados
        "filtros": {
            "nombre": nombre,
            "asignado": asignado_id,
            "estado_ejecucion": estado_ejecucion,
            "estado_asignacion": estado_asignacion,
            "habilitada": habilitada,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "avance_min": avance_min,
            "avance_max": avance_max,
        },
    }

    return render(request, "construccion1app/programacion.html", context)
    


    from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import date
from decimal import Decimal

@login_required
def exportar_actividades_excel(request, proyecto_id):
    """
    Exporta actividades a Excel con formato optimizado para Power BI
    Respeta todos los filtros aplicados en la vista
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    # === Capturar TODOS los filtros (igual que en programacion_obra) ===
    nombre = request.GET.get("nombre", "")
    asignado_id = request.GET.get("asignado", "")
    estado_ejecucion = request.GET.get("estado_ejecucion", "")
    estado_asignacion = request.GET.get("estado_asignacion", "")
    habilitada = request.GET.get("habilitada", "")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    avance_min = request.GET.get("avance_min", "")
    avance_max = request.GET.get("avance_max", "")
    nivel_id = request.GET.get("nivel", "")
    espacio_nombre = request.GET.get("espacio", "")

    # === Aplicar EXACTAMENTE los mismos filtros ===
    actividades_qs = Actividad.objects.filter(
        espacio__nivel__proyecto=proyecto
    ).select_related(
        'espacio__nivel',
        'asignado',
        'predecesora',
        'sucesora'
    )

    if nombre:
        actividades_qs = actividades_qs.filter(nombre__icontains=nombre)
    if asignado_id:
        actividades_qs = actividades_qs.filter(asignado_id=asignado_id)
    if estado_ejecucion:
        actividades_qs = actividades_qs.filter(estado_ejecucion=estado_ejecucion)
    if estado_asignacion:
        actividades_qs = actividades_qs.filter(estado_asignacion=estado_asignacion)
    if habilitada:
        actividades_qs = actividades_qs.filter(habilitada=(habilitada == "true"))
    if fecha_inicio:
        actividades_qs = actividades_qs.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        actividades_qs = actividades_qs.filter(fecha_fin__lte=fecha_fin)
    if avance_min:
        actividades_qs = actividades_qs.filter(avance__gte=avance_min)
    if avance_max:
        actividades_qs = actividades_qs.filter(avance__lte=avance_max)
    if nivel_id:
        actividades_qs = actividades_qs.filter(espacio__nivel_id=nivel_id)
    if espacio_nombre:
        actividades_qs = actividades_qs.filter(espacio__nombre__icontains=espacio_nombre)

    # === Crear archivo Excel ===
    wb = Workbook()
    ws = wb.active
    ws.title = "Actividades"

    # === Estilos para el encabezado ===
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2E5090", end_color="2E5090", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # === Definir columnas optimizadas para Power BI ===
    headers = [
        "ID_Actividad",
        "Proyecto",
        "Nivel",
        "Espacio",
        "Actividad",
        "Estado_Ejecucion",
        "Estado_Asignacion",
        "Avance_%",
        "Incidencia_%",
        "Avance_Ponderado",
        "Asignado_A",
        "Email_Asignado",
        "Fecha_Inicio",
        "Fecha_Fin",
        "Duracion_Dias",
        "Habilitada",
        "Aprobacion_Calidad",
        "Tiene_Foto",
        "Tiene_Justificacion",
        "Predecesora",
        "Sucesora",
        "Fecha_Exportacion"
    ]

    # === Escribir encabezados ===
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    # === Escribir datos ===
    row_num = 2
    for actividad in actividades_qs:
        # Calcular duración
        duracion = None
        if actividad.fecha_inicio and actividad.fecha_fin:
            duracion = (actividad.fecha_fin - actividad.fecha_inicio).days + 1

        # Avance ponderado
        avance_ponderado = float(actividad.calcular_avance_ponderado())

        # Datos del asignado
        asignado_nombre = actividad.asignado.username if actividad.asignado else ""
        asignado_email = actividad.asignado.email if actividad.asignado else ""

        # Fila de datos
        row_data = [
            actividad.id,
            proyecto.nombre,
            actividad.espacio.nivel.nombre,
            actividad.espacio.nombre,
            actividad.nombre,
            actividad.get_estado_ejecucion_display(),
            actividad.get_estado_asignacion_display(),
            float(actividad.avance),
            float(actividad.incidencia),
            avance_ponderado,
            asignado_nombre,
            asignado_email,
            actividad.fecha_inicio,
            actividad.fecha_fin,
            duracion,
            "Sí" if actividad.habilitada else "No",
            "Sí" if actividad.aprobacion_calidad else "No",

            "Sí" if actividad.justificacion else "No",
            actividad.predecesora.nombre if actividad.predecesora else "",
            actividad.sucesora.nombre if actividad.sucesora else "",
            date.today()
        ]

        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            cell.border = border
            
            # Alineación según tipo de dato
            if isinstance(value, (int, float, Decimal)):
                cell.alignment = Alignment(horizontal="right")
            elif isinstance(value, date):
                cell.alignment = Alignment(horizontal="center")
                cell.number_format = 'DD/MM/YYYY'
            else:
                cell.alignment = Alignment(horizontal="left")

        row_num += 1

    # === Ajustar anchos de columna ===
    column_widths = {
        'A': 12,  # ID
        'B': 20,  # Proyecto
        'C': 15,  # Nivel
        'D': 15,  # Espacio
        'E': 30,  # Actividad
        'F': 18,  # Estado Ejecución
        'G': 18,  # Estado Asignación
        'H': 10,  # Avance
        'I': 12,  # Incidencia
        'J': 15,  # Avance Ponderado
        'K': 20,  # Asignado
        'L': 25,  # Email
        'M': 13,  # Fecha Inicio
        'N': 13,  # Fecha Fin
        'O': 12,  # Duración
        'P': 11,  # Habilitada
        'Q': 16,  # Aprobación Calidad
        'S': 18,  # Tiene Justificación
        'T': 20,  # Predecesora
        'U': 20,  # Sucesora
        'V': 16,  # Fecha Exportación
    }

    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    # === Congelar primera fila ===
    ws.freeze_panes = 'A2'

    # === Preparar respuesta HTTP ===
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Nombre del archivo con fecha
    filename = f"Actividades_{proyecto.nombre}_{date.today().strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Guardar archivo
    wb.save(response)
    
    return response


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from webpush.models import PushInformation

# views.py
import json

@login_required
@require_POST
def suscribir_notificaciones(request):
    """
    Guarda la suscripción del usuario en la base de datos
    """
    try:
        subscription_data = json.loads(request.body)
        PushInformation.objects.update_or_create(
            user=request.user,
            defaults={'subscription_info': subscription_data}
        )
        return JsonResponse({"message": "Suscripción exitosa"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# views.py
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def base_view(request):
    """
    Renderiza la base y pasa la clave VAPID al template
    """
    context = {
        'VAPID_PUBLIC_KEY': settings.WEBPUSH_SETTINGS['VAPID_PUBLIC_KEY']
    }
    return render(request, 'construccion1app/base.html', context)