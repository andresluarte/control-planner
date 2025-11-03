from django.apps import AppConfig

class Construccion1AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'construccion1app'

    def ready(self):
        import construccion1app.signals  # 👈 Importar aquí, no arriba
