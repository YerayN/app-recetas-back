from django.db import models
from django.contrib.auth.models import User


# 🏠 HOGARES (unidad compartida)
class Hogar(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_invitacion = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.nombre


# 👥 PERFIL DE USUARIO (vincula usuario con hogar)
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="miembros")

    def __str__(self):
        return f"{self.user.username} ({self.hogar.nombre})"


# 🧂 MODELOS BASE EXISTENTES
class Unidad(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"

    def __str__(self):
        return self.abreviatura or self.nombre


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="recetas")  # 👈 nueva relación
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tiempo_preparacion = models.PositiveIntegerField(help_text="Tiempo en minutos")
    instrucciones = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    imagen = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.nombre


class IngredienteReceta(models.Model):
    receta = models.ForeignKey(Receta, related_name="ingredientes", on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT)
    cantidad = models.FloatField(null=True, blank=True)
    unidad = models.ForeignKey(Unidad, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.cantidad or ''} {self.unidad or ''} {self.ingrediente}".strip()


# 🗓️ PLAN SEMANAL (ahora vinculado a hogar)
class PlanSemanal(models.Model):
    DIA_CHOICES = [
        ("Lunes", "Lunes"),
        ("Martes", "Martes"),
        ("Miércoles", "Miércoles"),
        ("Jueves", "Jueves"),
        ("Viernes", "Viernes"),
        ("Sábado", "Sábado"),
        ("Domingo", "Domingo"),
    ]

    TIPO_COMIDA_CHOICES = [
        ("desayuno", "Desayuno"),
        ("almuerzo", "Almuerzo"),
        ("comida", "Comida"),
        ("merienda", "Merienda"),
        ("cena", "Cena"),
        ("snack", "Snack"),
    ]

    hogar = models.ForeignKey(Hogar, on_delete=models.CASCADE, related_name="planes")
    dia = models.CharField(max_length=20, choices=DIA_CHOICES)
    tipo_comida = models.CharField(max_length=20, choices=TIPO_COMIDA_CHOICES)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="planes")
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plan semanal"
        verbose_name_plural = "Planes semanales"
        unique_together = ("hogar", "dia", "tipo_comida", "receta")

    def __str__(self):
        return f"{self.hogar.nombre} - {self.dia} ({self.tipo_comida}): {self.receta.nombre}"
