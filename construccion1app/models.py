# app: core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser,Permission,Group
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from cloudinary.models import CloudinaryField

class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)
    administrador_empresa = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="empresas_administradas"
    )

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    # Tipos de usuario
    class TipoUsuario(models.TextChoices):
        superusuario = "superusuario", _("SuperUsuario")
        SUPERADMIN_EMPRESA = "superadmin_empresa", _("SuperAdministrador de empresa")
        ADMIN_EMPRESA = "admin_empresa", _("Administrador de Empresa")
        SUPERVISOR_CONSTRUCTOR = "supervisor_constructor", _("Supervisor / Constructor")
        CALIDAD = "calidad", _("Calidad")

    tipo_usuario = models.CharField(
        max_length=50,
        choices=TipoUsuario.choices,
        default=TipoUsuario.superusuario
    )

    # Cargos
    class Cargo(models.TextChoices):
        PROGRAMADOR_CONTROL_AVANCE = "programador_control_avance", _("Programador y control de avance")
        ADMIN_OBRA = "admin_obra", _("Administrador de obra")
        JEFE_OT = "jefe_ot", _("Jefe de Oficina Técnica")
        PERSONAL_CALIDAD = "personal_calidad", _("Personal de Calidad")
        JEFE_TERRENO = "jefe_terreno", _("Jefe de Terreno")
        SUPERVISOR = "supervisor", _("Supervisores")
        GERENTE_PROYECTO = "gerente_proyecto", _("Gerente de Proyecto")

    cargo = models.CharField(
        max_length=50,
        choices=Cargo.choices,
        null=True,
        blank=True
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios"
    )
    fcm_token = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_tipo_usuario_display()}"
    
class Proyecto(models.Model):
    RUBRO_CHOICES = [
        ("vivienda", "Vivienda"),
        ("infraestructura", "Infraestructura"),
        ("comercial", "Comercial"),
        ("industrial", "Industrial"),
        ("remodelacion", "Remodelación"),
        ("urbanizacion", "Urbanización"),
        ("obra_publica", "Obra Pública"),
        ("otros", "Otros"),
    ]

    REGION_CHOICES = [
        ("arica", "Arica y Parinacota"),
        ("tarapaca", "Tarapacá"),
        ("antofagasta", "Antofagasta"),
        ("atacama", "Atacama"),
        ("coquimbo", "Coquimbo"),
        ("valparaiso", "Valparaíso"),
        ("metropolitana", "Metropolitana de Santiago"),
        ("ohiggins", "Libertador Gral. Bernardo O'Higgins"),
        ("maule", "Maule"),
        ("nuble", "Ñuble"),
        ("biobio", "Biobío"),
        ("araucania", "La Araucanía"),
        ("rios", "Los Ríos"),
        ("lagos", "Los Lagos"),
        ("aysen", "Aysén del Gral. Carlos Ibáñez del Campo"),
        ("magallanes", "Magallanes y de la Antártica Chilena"),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="proyectos"
    )
    nombre = models.CharField(max_length=255)
    rubro = models.CharField(
        max_length=100,
        choices=RUBRO_CHOICES,
        blank=True,
        null=True
    )
    ubicacion = models.CharField(
        max_length=100,
        choices=REGION_CHOICES,
        blank=True,
        null=True
    )  # Regiones de Chile
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuarios_acceso = models.ManyToManyField(
        Usuario,
        blank=True,
        related_name="proyectos_acceso"
    )

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"

    def calcular_avance(self):
        total = sum([n.calcular_avance_ponderado() for n in self.niveles.all()])
        return total  # ya está ponderado



        
        
class Nivel(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name="niveles", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    incidencia = models.FloatField(help_text="Porcentaje de incidencia del nivel en el proyecto")

    def calcular_avance_ponderado(self):
        total = sum([e.calcular_avance_ponderado() for e in self.espacios.all()])
        return (total * Decimal(str(self.incidencia))) / Decimal("100")


    def __str__(self):
        return self.nombre


class Espacio(models.Model):
    nivel = models.ForeignKey(Nivel, related_name="espacios", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    incidencia = models.FloatField(help_text="Porcentaje de incidencia del espacio en el nivel")

    def calcular_avance_ponderado(self):
        total = sum([a.calcular_avance_ponderado() for a in self.actividades.all()])
        return (total * Decimal(str(self.incidencia))) / Decimal("100")




    def __str__(self):
        return self.nombre



from django.db import models

class Actividad(models.Model):
    espacio = models.ForeignKey(
        "Espacio",
        related_name="actividades",
        on_delete=models.CASCADE
    )
    nombre = models.CharField(max_length=100)
    avance = models.FloatField(
        help_text="Porcentaje de avance de la actividad",
        default=0.0
    )
    aprobacion_calidad = models.BooleanField(
        default=True,
        blank=False,
        null=False,
        help_text="Indica si la actividad requiere aprobación de calidad")


    incidencia = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))],
        help_text="Porcentaje de incidencia de la actividad en el espacio"
    )

    # Asignado a un usuario de tipo calidad
    asignado = models.ForeignKey(
        "Usuario",
        limit_choices_to={"tipo_usuario": "supervisor_constructor"},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades_asignadas"
    )

    # Flujo técnico
    ESTADO_EJECUCION_CHOICES = [
        ("no_ejecutada", "No ejecutada"),
        ("ejecucion", "En ejecución"),
        ("ejecutada", "Ejecutada"),
        ("revisada", "Revisada"),
        ("observada", "Observada"),
    ]
    estado_ejecucion = models.CharField(
        max_length=20,
        choices=ESTADO_EJECUCION_CHOICES,
        default="ejecucion"
    )

    # Flujo administrativo
    ESTADO_ASIGNACION_CHOICES = [
        ("POR_ASIGNAR", "Por asignar"),
        ("ASIGNADA", "Asignada"),
        ("NO_ASIGNADA", "No asignada"),
    ]
    estado_asignacion = models.CharField(
        max_length=20,
        choices=ESTADO_ASIGNACION_CHOICES,
        default="POR_ASIGNAR"
    )

    # Evidencias de calidad

    archivo_justificacion = CloudinaryField(
        'justificacion',
        folder="actividades/justificaciones/",
        null=True,
        blank=True,
        resource_type='raw',
        type='upload',  # ← Añade esto
        help_text="Archivo de justificación subida"
    )
    
    justificacion = models.TextField(
        null=True,
        blank=True,
        help_text="Justificación subida"
    )

    # Flujo de dependencias
    predecesora = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sucesoras",
        help_text="Actividad que debe completarse antes de iniciar esta"
    )
    sucesora = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predecesoras",
        help_text="Actividad que depende de esta para comenzar"
    )

    # Planificación
    fecha_inicio = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha planificada de inicio de la actividad"
    )
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha planificada de fin de la actividad"
    )
    
    habilitada = models.BooleanField(
        default=False,
        help_text="Indica si la actividad está habilitada para ser ejecutada"
    )

    def calcular_avance_ponderado(self):
        return (Decimal(str(self.avance)) * self.incidencia) / Decimal("100")
    
    information = models.BooleanField(
        default=False,
        help_text="Indica si la actividad requiere información adicional"
    )
    
    archivo_informacion = CloudinaryField(
        'informacion',
        folder="actividades/informacion_adicional/",
        null=True,
        blank=True,
        resource_type='raw',
        type='upload',  # ← Añade esto
        help_text="Archivo con información adicional para la actividad"     
    )

    def __str__(self):
        estado = "✅ Habilitada" if self.habilitada else "❌ No habilitada"
        return f"{self.nombre} - {self.get_estado_ejecucion_display()} - {estado}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(
        "Usuario",  # tu modelo propio
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )
    actividad = models.ForeignKey(Actividad, null=True, blank=True, on_delete=models.CASCADE)  # 👈 campo nuevo
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)  # 👈 nuevo campo opcional

    def __str__(self):
        return f"Notif. para {self.usuario.username}: {self.mensaje[:30]}"