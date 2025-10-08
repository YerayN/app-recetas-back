from django.contrib import admin
from .models import Unidad, Ingrediente, Receta, IngredienteReceta, PlanSemanal, Hogar, PerfilUsuario

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abreviatura")


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("nombre",)


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "hogar", "tiempo_preparacion", "creado_en")
    list_filter = ("hogar",)
    search_fields = ("nombre", "descripcion")


@admin.register(IngredienteReceta)
class IngredienteRecetaAdmin(admin.ModelAdmin):
    list_display = ("receta", "ingrediente", "cantidad", "unidad")


@admin.register(PlanSemanal)
class PlanSemanalAdmin(admin.ModelAdmin):
    list_display = ("hogar", "dia", "tipo_comida", "receta", "creado_por")
    list_filter = ("hogar", "dia", "tipo_comida")
    search_fields = ("receta__nombre",)


@admin.register(Hogar)
class HogarAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo_invitacion")
    search_fields = ("nombre", "codigo_invitacion")


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "hogar")
    list_filter = ("hogar",)
