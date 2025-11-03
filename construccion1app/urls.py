from django.urls import path
from .views import home, MisProyectosViewHome,login_view,logout_view,agregarusuario,lista_usuarios_empresa,lista_empresas,mi_perfil,dashboard_proyecto,agregar_proyecto,editar_visibilidad,agregar_nivel,agregar_espacio,agregar_actividad,modificar_actividad,detalle_notificacion,lista_notificaciones,mapa_actividades,incidencia_restante,importar_actividades
from .views import home, MisProyectosViewHome,sumar_incidencias,programacion_obra,eliminar_proyecto,eliminar_nivel,eliminar_espacio,eliminar_actividad,exportar_actividades_excel,suscribir_notificaciones
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', MisProyectosViewHome.as_view(), name='mis_proyectos'),
    path('mis-proyectos/', MisProyectosViewHome.as_view(), name='mis_proyectos'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('agregar-usuario/', agregarusuario, name='agregar_usuario'),
    path('usuarios-empresa/', lista_usuarios_empresa, name='lista_usuarios_empresa'),
    path('empresas/', lista_empresas, name='lista_empresas'),
    path('perfil/',mi_perfil, name='mi_perfil'),
    path('dashboard-proyecto/<int:proyecto_id>/', dashboard_proyecto, name='dashboard_proyecto'),
    path('agregar/', agregar_proyecto, name='agregar_proyecto'),
    path('proyecto/<int:proyecto_id>/visibilidad/', editar_visibilidad, name='editar_visibilidad'),
    path('agregar_nivel/<int:proyecto_id>/', agregar_nivel, name='agregar_nivel'),
    path('agregar_espacio/<int:nivel_id>/', agregar_espacio, name='agregar_espacio'),
    path('agregar_actividad/<int:espacio_id>/', agregar_actividad, name='agregar_actividad'),
    path('modificar_actividad/<int:actividad_id>/', modificar_actividad, name='modificar_actividad'),
    path('notificacion/<int:pk>/', detalle_notificacion, name='detalle_notificacion'),
    path('notificaciones/', lista_notificaciones, name='lista_notificaciones'),
    path('mapa_actividades/<int:espacio_id>/', mapa_actividades, name='mapa_actividades'), 
    path("incidencia-restante/<int:espacio_id>/", incidencia_restante, name="incidencia_restante"),
    path("espacio/<int:espacio_id>/importar-actividades/", importar_actividades, name="importar_actividades"),
    path(
        "proyecto/<int:proyecto_id>/sumar-incidencias/",
        sumar_incidencias,
        name="sumar_incidencias"
    ),
    path('proyecto/<int:proyecto_id>/programacion/', programacion_obra, name="programacion_obra"),
    path('proyecto/eliminar/<int:pk>/', eliminar_proyecto, name='eliminar_proyecto'),
    path('nivel/eliminar/<int:pk>/', eliminar_nivel, name='eliminar_nivel'),
    path('espacio/eliminar/<int:pk>/', eliminar_espacio, name='eliminar_espacio'),
    path('actividad/eliminar/<int:pk>/', eliminar_actividad, name='eliminar_actividad'),
    path(
        'proyecto/<int:proyecto_id>/exportar-actividades/',
        exportar_actividades_excel,
        name='exportar_actividades_excel'
    ),
    path('suscribir-notificaciones/', suscribir_notificaciones, name='suscribir_notificaciones'),
]






    




