from django.apps import AppConfig


class RecetasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recetas'

    # 👇 Esto hace que Django cargue las señales automáticamente
    def ready(self):
        import recetas.signals
