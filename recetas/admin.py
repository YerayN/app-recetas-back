from django.contrib import admin
from .models import Unidad, Ingrediente, Receta, IngredienteReceta, PlanSemanal, Hogar, PerfilUsuario
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

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
        from django.contrib import messages
        from django.shortcuts import render
        from django import forms

        class CategoriaForm(forms.Form):
            _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
            categoria = forms.ChoiceField(
                choices=Ingrediente.CATEGORIAS_CHOICES,
                label="Nueva categoría"
            )

        if 'apply' in request.POST:
            form = CategoriaForm(request.POST)
            if form.is_valid():
                nueva_categoria = form.cleaned_data['categoria']
                count = queryset.update(categoria=nueva_categoria)
                self.message_user(request, f"{count} ingredientes actualizados a '{nueva_categoria}'", level=messages.SUCCESS)
                return None
        else:
            form = CategoriaForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})

        return render(request, 'admin/cambiar_categoria.html', {'form': form, 'ingredientes': queryset})



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
