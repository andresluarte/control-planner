# construccion1app/forms.py
from django import forms
from .models import Usuario
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuario',
            'class': 'form-control',
            'style': 'background-color: #ede3ae;'
        })
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control',
            'style': 'background-color: #ede3ae;'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quitar los asteriscos de campos obligatorios
        self.required_css_class = ''
        self.error_css_class = 'is-invalid'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Ingresar', css_class='btn btn-primary w-100'))
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
        )

class AgregarUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name','cargo' ,'email', 'password', 'tipo_usuario']

    def __init__(self, *args, **kwargs):
        self.creador = kwargs.pop('creador', None)
        super().__init__(*args, **kwargs)

        # Filtrar opciones de tipo_usuario según el creador
        if self.creador:
            opciones = []

            if self.creador.tipo_usuario == "superadmin_empresa":
                # SuperAdmin puede crear AdminEmpresa, Supervisor y Calidad
                permitir = ["admin_empresa", "supervisor_constructor", "calidad"]
            elif self.creador.tipo_usuario == "admin_empresa":
                # AdminEmpresa solo puede crear Supervisor y Calidad
                permitir = ["admin_empresa","supervisor_constructor", "calidad"]
            else:
                permitir = []

            for key, label in Usuario.TipoUsuario.choices:
                if key in permitir:
                    opciones.append((key, label))

            self.fields['tipo_usuario'].choices = opciones

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Encriptar contraseña
        if commit:
            user.save()
        return user

from django import forms
from .models import Proyecto,Nivel,Espacio,Actividad


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre','rubro','ubicacion','descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


class NivelForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = ['nombre', 'incidencia']  # excluimos 'proyecto' si lo asignas en la vista

    def __init__(self, *args, **kwargs):
        self.proyecto = kwargs.pop("proyecto", None)  # pasamos el proyecto desde la vista
        super().__init__(*args, **kwargs)

    def clean_incidencia(self):
        incidencia = self.cleaned_data.get("incidencia", 0)

        if self.proyecto:
            # Suma actual de incidencias del proyecto (excluyendo el mismo objeto si está en edición)
            qs = Nivel.objects.filter(proyecto=self.proyecto)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            suma_existente = qs.aggregate(total=Sum("incidencia"))["total"] or 0

            if suma_existente + incidencia > 100:
                raise ValidationError(
                    f"La suma de incidencias supera 100. Actualmente tienes {suma_existente}, "
                    f"y al agregar {incidencia} llegarías a {suma_existente + incidencia}."
                )

        return incidencia

class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = [ 'nombre', 'incidencia']

    def __init__(self, *args, **kwargs):
        self.nivel = kwargs.pop('nivel', None)
        super().__init__(*args, **kwargs)

    def clean_incidencia(self):
        incidencia = self.cleaned_data['incidencia']
        if self.nivel:
            total_actual = Espacio.objects.filter(
                nivel=self.nivel
            ).exclude(
                id=self.instance.id
            ).aggregate(total=Sum('incidencia'))['total'] or 0

            if total_actual + incidencia > 100:
                raise ValidationError(
                    f"La suma total de incidencias ({total_actual + incidencia}) no puede superar 100."
                )
        return incidencia


from django import forms
from .models import Actividad, Usuario

from django.db.models import Sum   # 👈 importante

from django.core.exceptions import ValidationError

class ActividadForm(forms.ModelForm):     
    class Meta:         
        model = Actividad         
        fields = "__all__" 
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):         
        user = kwargs.pop('user', None)
        espacio = kwargs.pop('espacio', None)  # Recibir espacio como parámetro
        super().__init__(*args, **kwargs)          
        
        if user:             
            self.fields['asignado'].queryset = Usuario.objects.filter(                 
                tipo_usuario='supervisor_constructor',                 
                empresa=user.empresa             
            )          
            
        # Manejar filtrado de predecesora y sucesora
        espacio_id = None
        
        # Obtener espacio_id de diferentes fuentes
        if espacio:
            espacio_id = espacio.id
        elif hasattr(self.instance, 'espacio') and self.instance.espacio:
            espacio_id = self.instance.espacio.id
        elif hasattr(self.instance, 'espacio_id') and self.instance.espacio_id:
            espacio_id = self.instance.espacio_id
            
        if espacio_id:
            # Para actividad existente, excluir la actividad actual
            if self.instance.pk:
                actividades_mismo_espacio = Actividad.objects.filter(
                    espacio_id=espacio_id
                ).exclude(id=self.instance.id)
            else:
                # Para nueva actividad, incluir todas las actividades del espacio
                actividades_mismo_espacio = Actividad.objects.filter(espacio_id=espacio_id)
                
            self.fields['predecesora'].queryset = actividades_mismo_espacio             
            self.fields['sucesora'].queryset = actividades_mismo_espacio
        else:             
            self.fields['predecesora'].queryset = Actividad.objects.none()             
            self.fields['sucesora'].queryset = Actividad.objects.none()
            
        # Si se pasa un espacio, establecerlo como valor inicial
        if espacio:
            self.fields['espacio'].initial = espacio
            self.fields['espacio'].disabled = True  # No permitir cambiar el espacio
    

    def clean_incidencia(self):         
        incidencia = self.cleaned_data.get("incidencia", 0)         
        espacio = self.cleaned_data.get("espacio")          
        
        if espacio:
            # Si es una actividad nueva
            if not self.instance.pk:
                total_otras = espacio.actividades.aggregate(
                    total=Sum("incidencia")
                )["total"] or 0
            else:
                # Si es una actividad existente, excluirla del cálculo
                total_otras = espacio.actividades.exclude(id=self.instance.id).aggregate(                 
                    total=Sum("incidencia")             
                )["total"] or 0              
            
            if total_otras + incidencia > 100:                 
                restante = max(0, 100 - total_otras)                 
                raise ValidationError(                     
                    f"Las demás actividades suman {total_otras}%. "                     
                    f"Tu actividad debería tener {restante}% para llegar a 100%."                 
                )         
        return incidencia
    def clean_archivo_informacion(self):
        archivo = self.cleaned_data.get('archivo_informacion')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Solo se permiten archivos PDF.')
            # Opcional: validar tamaño (ej: máximo 10MB)
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar 10MB.')
        return archivo
    
    def save(self, commit=True):
        """Sobrescribir save para manejar la lógica de predecesora-sucesora"""
        # Determinar si es una actividad nueva o existente
        es_nueva = not self.instance.pk
        
        # Para actividades existentes, obtener estado anterior
        estado_anterior = None
        predecesora_anterior = None
        
        if not es_nueva:
            try:
                actividad_anterior = Actividad.objects.get(pk=self.instance.pk)
                estado_anterior = actividad_anterior.estado_ejecucion
                predecesora_anterior = actividad_anterior.predecesora
            except Actividad.DoesNotExist:
                estado_anterior = None
                predecesora_anterior = None
        
        # Guardar la predecesora actual antes de guardar la instancia
        predecesora_actual = self.cleaned_data.get('predecesora')
        
        # Primero guardar la actividad para que tenga un ID válido
        instance = super().save(commit=commit)
        
        # Solo proceder si commit=True (la instancia está realmente guardada)
        if commit:
            # 🆕 LÓGICA PARA PREDECESORA-SUCESORA
            # Si se cambió la predecesora o se asignó una nueva (tanto para crear como modificar)
            if predecesora_anterior != predecesora_actual:
                
                # Si había una predecesora anterior, quitar esta actividad como su sucesora
                if predecesora_anterior and predecesora_anterior.sucesora == instance:
                    predecesora_anterior.sucesora = None
                    predecesora_anterior.save()
                
                # Si hay una nueva predecesora, establecer esta actividad como su sucesora
                if predecesora_actual:
                    # Solo establecer la relación si la predecesora no tiene ya una sucesora
                    if not predecesora_actual.sucesora:
                        predecesora_actual.sucesora = instance
                        predecesora_actual.save()
                        
                        # Mensaje para mostrar en template
                        self.relacion_establecida = f"La actividad '{predecesora_actual.nombre}' ahora tiene como sucesora a '{instance.nombre}'"
                    else:
                        # Opcional: Decidir si sobrescribir o no
                        # predecesora_actual.sucesora = instance
                        # predecesora_actual.save()
                        self.relacion_establecida = f"La actividad '{predecesora_actual.nombre}' ya tenía una sucesora. No se modificó."
                else:
                    self.relacion_establecida = None
            else:
                self.relacion_establecida = None
            
            # 🔄 LÓGICA PARA HABILITAR SUCESORAS (solo para modificaciones)
            if not es_nueva and (estado_anterior != 'ejecutada' and 
                instance.estado_ejecucion == 'ejecutada' and 
                instance.sucesora):
                
                # Habilitar la actividad sucesora
                instance.sucesora.habilitada = True
                instance.sucesora.save()
                
                # Almacenar el nombre de la sucesora en el formulario para mostrarlo en el template
                self.sucesora_habilitada_nombre = instance.sucesora.nombre
            else:
                self.sucesora_habilitada_nombre = None
            
        return instance


class ModificarActividadForm(forms.ModelForm):     
    class Meta:         
        model = Actividad         
        fields = [             
            'espacio', 'nombre', 'avance', 'incidencia','aprobacion_calidad',       
            'asignado', 'estado_ejecucion', 'estado_asignacion',             
            'justificacion', 'predecesora', 'sucesora','archivo_justificacion',          
            'fecha_inicio','fecha_fin','habilitada','archivo_informacion',
        ]      
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):         
        user = kwargs.pop('user', None)         
        super().__init__(*args, **kwargs)          
        
        # Espacio como solo lectura         
        self.fields['espacio'].disabled = True
        
        # ========================================
        # 🔒 BLOQUEO TOTAL SI ESTÁ REVISADA
        # ========================================
        if self.instance and self.instance.pk and self.instance.estado_ejecucion == 'revisada':
            # Deshabilitar TODOS los campos
            for field_name, field in self.fields.items():
                field.disabled = True
                # Agregar clase visual para indicar que está bloqueado
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs['readonly'] = True
                    field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' bg-light'
                    field.widget.attrs['data-revisada'] = 'true'  # ← AÑADIR ESTE ATRIBUTO
            
            # Mensaje informativo
            self.mensaje_revisada = "Esta actividad está revisada y no puede ser modificada."
            self.esta_revisada = True  # ← AÑADIR ESTE ATRIBUTO
            
            # Salir temprano
            return
        else:
            self.esta_revisada = False  # ← AÑADIR ESTE ATRIBUTO
        
    # ... resto del código ...
                   
        # ✅ Habilitar sucesora si la actividad está ejecutada         
        if self.instance.estado_ejecucion == 'ejecutada':             
            if 'sucesora' in self.fields:                 
                self.fields['sucesora'].widget = forms.Select(                     
                    choices=self.fields['sucesora'].choices                 
                )           
                
        if user:             
            # ========================================
            # 🔒 RESTRICCIONES PARA CALIDAD Y SUPERVISOR_CONSTRUCTOR
            # ========================================
            if user.tipo_usuario in ['calidad','supervisor_constructor']:                 
                # Campos que deben ocultarse (NO incluir fechas aquí)
                campos_ocultos = [                     
                    'incidencia', 'asignado', 'estado_asignacion', 'aprobacion_calidad',                 
                    'predecesora', 'sucesora', 'habilitada'                
                ]                 
                for campo in campos_ocultos:                     
                    if campo in self.fields:                         
                        self.fields[campo].widget = forms.HiddenInput()
                
                # ✅ SOLUCIÓN: Eliminar fechas del formulario para estos usuarios
                # Esto evita que se borren al guardar
                if 'fecha_inicio' in self.fields:
                    del self.fields['fecha_inicio']
                if 'fecha_fin' in self.fields:
                    del self.fields['fecha_fin']
                
                # Campos de solo lectura
                campo_solo_lectura = ['nombre']                 
                for campo in campo_solo_lectura:                     
                    if campo in self.fields:                         
                        self.fields[campo].disabled = True
            if user.tipo_usuario == 'calidad':
                if 'avance' in self.fields:
                    self.fields['avance'].widget.attrs['readonly'] = True
            # ========================================
            # 🔒 RESTRICCIÓN PARA SUPERVISOR_CONSTRUCTOR - ARCHIVOS
            # No puede modificar archivo_justificacion ni archivo_informacion
            # ========================================
            if user.tipo_usuario == 'supervisor_constructor':
                # Deshabilitar campos de archivo para que no puedan modificarse
                if 'archivo_justificacion' in self.fields:
                    self.fields['archivo_justificacion'].disabled = True
                    self.fields['archivo_justificacion'].widget.attrs['readonly'] = True
                    
                if 'archivo_informacion' in self.fields:
                    self.fields['archivo_informacion'].disabled = True
                    self.fields['archivo_informacion'].widget.attrs['readonly'] = True
            
            # ========================================
            # 🔒 RESTRICCIÓN PARA SUPERVISOR_CONSTRUCTOR - ESTADOS
            # No puede seleccionar: observada, revisada, no_ejecutada, en_ejecucion
            # ========================================
            if user.tipo_usuario == 'supervisor_constructor':
                # Obtener el estado actual de la actividad
                estado_actual = None
                if self.instance and self.instance.pk:
                    estado_actual = self.instance.estado_ejecucion
                
                # Definir las opciones permitidas para supervisor
                # NUNCA puede seleccionar: observada, revisada, no_ejecutada, en_ejecucion
                opciones_prohibidas = ['observada', 'revisada', 'no_ejecutada', 'en_ejecucion']
                
                # Filtrar las opciones del campo estado_ejecucion
                opciones_filtradas = [
                    (key, value) 
                    for key, value in self.fields['estado_ejecucion'].choices
                    if key not in opciones_prohibidas
                ]
                
                # Si la actividad ya está observada, mantenerla como opción
                if estado_actual == 'observada':
                    # Agregar 'observada' a las opciones
                    opciones_filtradas.insert(0, ('observada', 'Observada (actual)'))
                    self.fields['estado_ejecucion'].widget = forms.Select(
                        choices=opciones_filtradas,
                        attrs={'class': 'form-control'}
                    )
                else:
                    # Aplicar las opciones filtradas
                    self.fields['estado_ejecucion'].widget = forms.Select(
                        choices=opciones_filtradas,
                        attrs={'class': 'form-control'}
                    )
                        
            # Filtrar usuarios que puedan asignarse             
            self.fields['asignado'].queryset = Usuario.objects.filter(                 
                tipo_usuario='supervisor_constructor',                 
                empresa=user.empresa             
            )                   
            
        # Configuraciones que dependen de la instancia existente         
        if self.instance and hasattr(self.instance, 'pk') and self.instance.pk:             
            # Solo habilitar justificación si estado = "observada"             
            if self.instance.estado_ejecucion != 'observada':                 
                self.fields['justificacion'].disabled = True               
                
            # Limitar predecesora y sucesora a actividades del mismo espacio             
            if self.instance.espacio:                 
                mismo_espacio = self.instance.espacio.actividades.exclude(                     
                    id=self.instance.id                 
                )                 
                self.fields['predecesora'].queryset = mismo_espacio                 
                self.fields['sucesora'].queryset = mismo_espacio
    
    def clean_archivo_informacion(self):
        archivo = self.cleaned_data.get('archivo_informacion')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Solo se permiten archivos PDF.')
            # Opcional: validar tamaño (ej: máximo 10MB)
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar 10MB.')
        return archivo
    
    def clean_estado_ejecucion(self):
        """Validación adicional para supervisor_constructor"""
        estado = self.cleaned_data.get('estado_ejecucion')
        
        # Obtener el usuario desde el request (se debe pasar al formulario)
        user = getattr(self, 'user', None)
        
        if user and user.tipo_usuario == 'supervisor_constructor':
            # Estados prohibidos para supervisor
            estados_prohibidos = ['observada', 'revisada', 'no_ejecutada','en_ejecucion']
            
            # Si intenta seleccionar un estado prohibido
            if estado in estados_prohibidos:
                raise forms.ValidationError(
                    f'No tienes permiso para marcar la actividad como "{estado}". '
                    f'Solo puedes marcar como "ejecutada".'
                )
        
        return estado
    
    def clean_archivo_justificacion(self):
        """Validación similar para archivo_justificacion si es necesario"""
        archivo = self.cleaned_data.get('archivo_justificacion')
        
        # Si no hay archivo nuevo, retornar el existente
        if not archivo:
            return archivo
        
        # Si es un archivo nuevo subido
        if hasattr(archivo, 'name'):
            # Validar tamaño (máximo 10MB)
            if hasattr(archivo, 'size') and archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar 10MB.')
        
        return archivo
                
    def clean_incidencia(self):         
        incidencia = self.cleaned_data.get("incidencia", 0)         
        espacio = self.cleaned_data.get("espacio")          
        
        if espacio:             
            total_otras = espacio.actividades.exclude(id=self.instance.id).aggregate(                 
                total=Sum("incidencia")             
            )["total"] or 0              
            
            if total_otras + incidencia > 100:                 
                restante = max(0, 100 - total_otras)                 
                raise ValidationError(                     
                    f"Las demás actividades suman {total_otras}%. "                     
                    f"Tu actividad debería tener {restante}% para llegar a 100%."                 
                )         
        return incidencia
    
    def save(self, commit=True):
        """Sobrescribir save para manejar la lógica de habilitación de sucesoras"""
        # Obtener el estado anterior si la instancia ya existe
        estado_anterior = None
        if self.instance.pk:
            try:
                actividad_anterior = Actividad.objects.get(pk=self.instance.pk)
                estado_anterior = actividad_anterior.estado_ejecucion
            except Actividad.DoesNotExist:
                estado_anterior = None
        
        # Guardar la actividad
        instance = super().save(commit=commit)
        
        # Si el estado cambió a 'ejecutada' y hay una sucesora
        if (estado_anterior != 'ejecutada' and 
            instance.estado_ejecucion == 'ejecutada' and 
            instance.sucesora):
            
            # Habilitar la actividad sucesora
            instance.sucesora.habilitada = True
            instance.sucesora.save()
            
            # Almacenar el nombre de la sucesora en el formulario para mostrarlo en el template
            self.sucesora_habilitada_nombre = instance.sucesora.nombre
        else:
            self.sucesora_habilitada_nombre = None
            
        return instance