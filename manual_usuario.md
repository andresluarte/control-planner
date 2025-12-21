# Manual de Usuario - Sistema de Gestión de Construcción

## Introducción

Bienvenido al Sistema de Gestión de Construcción, una aplicación web diseñada para facilitar la administración y seguimiento de proyectos de construcción. Este sistema permite gestionar proyectos, niveles, espacios y actividades de manera jerárquica, con control de permisos basado en roles de usuario.

### Propósito del Sistema
- **Gestión de Proyectos**: Crear y administrar proyectos de construcción con estructura jerárquica (Proyecto > Nivel > Espacio > Actividad).
- **Seguimiento de Avances**: Monitorear el progreso de actividades mediante porcentajes de avance e incidencia.
- **Control de Permisos**: Diferentes niveles de acceso según el rol del usuario.
- **Notificaciones**: Sistema de notificaciones push para mantener informados a los usuarios.
- **Reportes**: Exportación de datos a Excel para análisis en Power BI.

### Requisitos del Sistema
- Navegador web moderno (Chrome, Firefox, Edge).
- Conexión a internet para notificaciones push.
- Permisos adecuados según su rol en la empresa.

## Roles de Usuario

El sistema cuenta con los siguientes roles, cada uno con permisos específicos:

### 1. Superusuario (Administrador del Sistema)
- Acceso completo a todas las funcionalidades.
- Puede gestionar empresas y usuarios globales.
- Acceso a eliminación de proyectos, niveles y espacios.

### 2. SuperAdminEmpresa
- Administrador principal de una empresa.
- Puede crear y gestionar proyectos, niveles, espacios y actividades.
- Gestiona usuarios de la empresa (excepto otros SuperAdmin).
- Acceso a eliminación de elementos.

### 3. AdminEmpresa
- Administrador de empresa.
- Gestiona proyectos, niveles, espacios y actividades.
- Puede crear usuarios (supervisores y calidad).
- No puede eliminar proyectos existentes.

### 4. SupervisorConstructor
- Usuario operativo en obra.
- Puede ver proyectos asignados.
- Modificar actividades asignadas (con restricciones).
- No puede crear proyectos o gestionar estructura jerárquica.

### 5. Calidad
- Control de calidad.
- Acceso limitado a modificación de actividades.
- Enfoque en aprobación y control de calidad.


## Inicio de Sesión

1. Acceda a la URL del sistema.
2. Ingrese su nombre de usuario y contraseña.
3. Haga clic en "Ingresar".
4. Si las credenciales son correctas, será redirigido al dashboard de proyectos.

### Recuperación de Contraseña
- Contacte a su administrador de empresa para cambiar la contraseña.

## Navegación Principal

### Dashboard de Proyectos (Mis Proyectos)
- **Vista principal**: Lista todos los proyectos accesibles según su rol.
- **Información mostrada**: Nombre del proyecto, avance total, empresa.
- **Acciones disponibles**:
  - Ver dashboard detallado del proyecto.
  - Filtrar por empresa (solo Superusuario).

### Dashboard de Proyecto Detallado
- **Gráfico principal**: Muestra el avance total del proyecto en formato de dona.
- **Estructura jerárquica**:
  - **Niveles**: Divisiones principales del proyecto.
  - **Espacios**: Subdivisiones dentro de niveles.
  - **Actividades**: Tareas específicas dentro de espacios.

#### Funcionalidades por Rol

##### Para Superusuario y SuperAdminEmpresa:
- **Eliminar Proyecto**: Botón rojo para eliminar el proyecto completo.
- **Crear Nivel**: Formulario colapsable para agregar nuevos niveles.
- **Por Nivel**:
  - Ver badges de incidencia y ponderado.
  - Eliminar nivel.
  - Agregar espacio.
- **Por Espacio**:
  - Eliminar espacio.
  - Ver badge de incidencia.
  - Agregar actividad.
  - Importar actividades desde Excel.
  - Descargar plantilla Excel.
  - Ver mapa de actividades.
- **Tabla de Actividades**:
  - Ver todas las columnas (incidencia, ponderado).
  - Modificar cualquier actividad.
  - Eliminar actividades.

##### Para AdminEmpresa:
- Crear nivel.
- Agregar espacios a niveles.
- Gestionar actividades (agregar, modificar, importar).
- Ver mapa de actividades.

##### Para SupervisorConstructor y Calidad:
- Ver proyectos asignados.
- Modificar actividades asignadas (con restricciones).
- Ver mapa de actividades.


## Gestión de Proyectos

### Crear Proyecto
1. Desde "Mis Proyectos", acceder a la opción de crear proyecto (según permisos).
2. Completar formulario: nombre, rubro, ubicación, descripción, fechas.
3. Guardar.

### Ver Dashboard de Proyecto
1. Hacer clic en el nombre del proyecto desde "Mis Proyectos".
2. Visualizar:
   - Gráfico de avance total.
   - Lista de niveles con barras de progreso.
   - Espacios colapsables con actividades.

## Gestión de Niveles

### Crear Nivel
1. En dashboard de proyecto, hacer clic en "Crear Nivel".
2. Ingresar nombre e incidencia (porcentaje del proyecto).
3. Validación automática: suma de incidencias no puede superar 100%.

### Ver/Editar Nivel
- Ver avance calculado automáticamente.
- Eliminar nivel (según permisos).

## Gestión de Espacios

### Crear Espacio
1. En un nivel, hacer clic en "Agregar Espacio".
2. Ingresar nombre e incidencia (porcentaje del nivel).
3. Validación: suma no puede superar 100%.

### Funcionalidades de Espacio
- **Gráfico de avance**: Dona que muestra progreso.
- **Actividades**: Lista colapsable con tabla detallada.

## Gestión de Actividades

### Crear Actividad
1. En un espacio, hacer clic en "+" si la suma de incidencias < 100%.
2. Completar formulario:
   - Nombre, avance, incidencia.
   - Asignado (supervisor de la empresa).
   - Estados de ejecución y asignación.
   - Fechas de inicio y fin.
   - Predecesora/sucesora (relaciones de dependencia).
   - Archivos (justificación PDF, información PDF).
3. Validaciones automáticas.

### Modificar Actividad
1. Hacer clic en el botón de lápiz (✏️) en la fila de la actividad en la tabla.
2. Se abrirá el formulario de modificación con los campos disponibles según su rol:
   - **Campos comunes**: Nombre, avance, incidencia, estado de ejecución, estado de asignación, justificación, predecesora/sucesora, fechas de inicio/fin, archivos.
   - **Campos restringidos**:
     - **Para Calidad y Supervisor**: No pueden modificar incidencia, asignado, estado de asignación, aprobación de calidad, predecesora/sucesora, habilitada, fechas.
     - **Para Supervisor**: No puede modificar archivos de justificación e información.
3. Realizar los cambios necesarios.
4. Hacer clic en "Guardar".
5. Si se marca como "Ejecutada", las actividades sucesoras se habilitarán automáticamente.
6. Si hay errores de validación (ej: suma de incidencias > 100%), se mostrarán mensajes específicos.

### Estados de Actividad
- **No ejecutada**: Inicial.
- **En ejecución**: En progreso.
- **Ejecutada**: Completada (habilita sucesoras automáticamente).
- **Observada**: Requiere justificación.
- **Revisada**: Aprobada por calidad.

### Importar Actividades
Esta función permite cargar múltiples actividades desde un archivo Excel de manera masiva.

#### Paso 1: Descargar Plantilla
1. En el dashboard de proyecto, hacer clic en "Descargar Plantilla" en la sección de un espacio.
2. Se descargará un archivo Excel con las columnas requeridas y datos de ejemplo.

#### Paso 2: Formato del Archivo Excel
El archivo debe tener exactamente las siguientes columnas en este orden:

| Columna | Tipo | Descripción | Valores Permitidos |
|---------|------|-------------|-------------------|
| **nombre** | Texto | Nombre de la actividad | Texto único, no vacío |
| **avance** | Número | Porcentaje de avance | Solo 0 o 100 |
| **incidencia** | Número decimal | Porcentaje de importancia | Número positivo (ej: 25.5) |
| **estado_ejecucion** | Texto | Estado actual | no_ejecutada, ejecucion, ejecutada, revisada, observada |
| **estado_asignacion** | Texto | Estado de asignación | POR_ASIGNAR, ASIGNADA, NO_ASIGNADA |
| **habilitada** | Booleano | Si está habilitada | True/False, 1/0, Si/No |

**Notas importantes**:
- **Fila 1**: Encabezados exactamente como se indica (case-sensitive).
- **Filas 2 en adelante**: Datos de actividades.
- **Suma de incidencias**: Debe ser exactamente 100.00.
- **Nombres únicos**: No puede haber actividades con el mismo nombre en el mismo espacio.
- **Sin celdas vacías**: Todas las celdas deben tener valores.

#### Paso 3: Subir Archivo
1. Hacer clic en "Importar Actividades" en la sección de un espacio.
2. Seleccionar el archivo Excel completado.
3. Hacer clic en "Subir".
4. El sistema validará automáticamente:
   - Presencia de todas las columnas.
   - Tipos de datos correctos.
   - Valores permitidos.
   - Suma de incidencias = 100.
   - Nombres únicos.
5. Si hay errores, se mostrarán mensajes específicos indicando la fila y columna problemática.
6. Si es válido, se crearán todas las actividades y se mostrará el número importado.

### Exportar Actividades
1. En dashboard de proyecto, opción de exportar.
2. Aplicar filtros si es necesario.
3. Descargar Excel optimizado para Power BI.

## Programación de Obra

Esta funcionalidad permite visualizar y gestionar la programación de actividades de un proyecto de manera organizada.

### Acceso
- Disponible solo para roles **SuperAdminEmpresa** y **AdminEmpresa**.

### Vista Kanban
- **Columnas**: Organizadas por estados de ejecución (No ejecutada, En ejecución, Ejecutada, Observada, Revisada).
- **Tarjetas**: Cada actividad muestra información clave como nombre, asignado, fechas y duración.

### Filtros Disponibles
- **Nombre**: Buscar actividades por nombre.
- **Asignado**: Filtrar por usuario asignado.
- **Estado de Ejecución**: Seleccionar estado específico.
- **Estado de Asignación**: Filtrar por asignación.
- **Habilitada**: Mostrar solo actividades habilitadas o no.
- **Fechas**: Rango de fecha de inicio y fin.
- **Avance**: Rango de porcentaje de avance.
- **Nivel/Espacio**: Filtrar por nivel o espacio específico.

### Navegación
1. Desde el dashboard de proyecto, acceder al enlace "Programación".
2. Aplicar filtros según necesidad.
3. Cambiar vista entre Kanban y lista si está disponible.

### Vista Gantt
- **Descripción**: Vista gráfica que muestra las actividades en un diagrama de Gantt, representando el tiempo y las dependencias entre actividades.
- **Condición**: Solo aparecen las actividades que tienen tanto la fecha de inicio como la fecha de fin completas.
- **Acceso**: Desde la vista de Programación, seleccionar la opción "Gantt".
- **Funcionalidades**: Permite visualizar la duración de las actividades, dependencias predecesora/sucesora, y el progreso a lo largo del tiempo.

## Mapa de Actividades

- Visualización gráfica de dependencias entre actividades.
- Nodos coloreados según estado.
- Interacción: arrastrar, zoom, detalles al hacer clic.

## Notificaciones

### Ver Notificaciones
- Icono en la barra superior muestra contador de no leídas.
- Lista paginada de notificaciones.
- Marcar como leída al abrir.

### Tipos de Notificación
- Cambios en actividades asignadas.
- Actividades habilitadas por predecesoras.
- Recordatorios de tareas pendientes.

### Notificaciones Push
- Configuración automática al iniciar sesión.
- Alertas en tiempo real en el navegador.

## Glosario

- **Proyecto**: Entidad principal que agrupa niveles.
- **Nivel**: División principal (ej: pisos, secciones).
- **Espacio**: Subdivisión dentro de nivel (ej: habitaciones, áreas).
- **Actividad**: Tarea específica con avance e incidencia.
- **Incidencia**: Porcentaje de importancia dentro del padre.
- **Avance**: Porcentaje de completitud.
- **Ponderado**: Avance calculado considerando incidencia.
- **Predecesora/Sucesora**: Relaciones de dependencia entre actividades.

## Solución de Problemas

### No puedo acceder a una funcionalidad
- Verificar su rol de usuario con el administrador.
- Algunos elementos requieren permisos específicos.

### Error al subir archivos
- Verificar formato (PDF para información/justificación).
- Tamaño máximo: 10MB.

### Gráficos no se muestran correctamente
- Actualizar página.
- Verificar conexión a internet para Chart.js.

### Notificaciones no llegan
- Verificar permisos del navegador para notificaciones.
- Recargar página para renovar token FCM.

## Soporte

Para soporte técnico:
- Contactar al administrador de su empresa.
- Para Superusuarios: acceder al panel de administración de Django.

---

*Este manual está basado en la versión actual del sistema. Las funcionalidades pueden variar según actualizaciones.*