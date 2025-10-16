from django.contrib import admin
from .models import Unidad, Ingrediente, Receta, IngredienteReceta, PlanSemanal, Hogar, PerfilUsuario

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abreviatura")


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria")  
    list_filter = ("categoria",)            
    search_fields = ("nombre",)
    actions = ["cambiar_categoria"]

    @admin.action(description="Cambiar categoría seleccionada")
    def cambiar_categoria(self, request, queryset):
        from django.shortcuts import render, redirect
        from django import forms

        class CategoriaForm(forms.Form):
            categoria = forms.ChoiceField(
                choices=Ingrediente.CATEGORIAS_CHOICES,
                label="Nueva categoría"
            )

        if "aplicar" in request.POST:
            form = CategoriaForm(request.POST)
            if form.is_valid():
                nueva_categoria = form.cleaned_data["categoria"]
                queryset.update(categoria=nueva_categoria)
                self.message_user(
                    request, 
                    f"{queryset.count()} ingredientes actualizados a la categoría '{nueva_categoria}'."
                )
                return redirect(request.get_full_path())

        else:
            form = CategoriaForm()

        return render(request, "admin/cambiar_categoria.html", {"form": form, "ingredientes": queryset})


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
