# construccion1app/management/commands/limpiar_tokens_fcm.py
from django.core.management.base import BaseCommand
from construccion1app.models import Usuario

class Command(BaseCommand):
    help = 'Limpia todos los tokens FCM para forzar renovación'

    def handle(self, *args, **kwargs):
        count = Usuario.objects.filter(fcm_token__isnull=False).update(fcm_token=None)
        self.stdout.write(
            self.style.SUCCESS(f'✅ {count} tokens FCM eliminados')
        )