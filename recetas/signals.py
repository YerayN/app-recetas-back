from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario, Hogar
import secrets


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Cada vez que se crea un usuario nuevo, se le asigna automáticamente un hogar
    y su perfil de usuario vinculado.
    """
    if created:
        # Crear un hogar propio con un código de invitación único
        hogar = Hogar.objects.create(
            nombre=f"Hogar de {instance.username}",
            codigo_invitacion=secrets.token_hex(4).upper()
        )

        # Crear el perfil del usuario vinculado a ese hogar
        PerfilUsuario.objects.create(user=instance, hogar=hogar)
