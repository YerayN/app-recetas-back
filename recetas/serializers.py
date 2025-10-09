from rest_framework import serializers
from .models import Receta, Ingrediente, Unidad, IngredienteReceta, PlanSemanal


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = ['id', 'nombre', 'abreviatura']


class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = ["id", "nombre", "categoria"]


# 🔹 Sub-serializador: detalle de ingrediente dentro de receta
class IngredienteRecetaSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del ingrediente y la unidad
    ingrediente_nombre = serializers.CharField(source="ingrediente.nombre", read_only=True)
    unidad_nombre = serializers.CharField(source="unidad.nombre", read_only=True)

    class Meta:
        model = IngredienteReceta
        fields = ["id", "ingrediente", "ingrediente_nombre", "cantidad", "unidad", "unidad_nombre"]


class RecetaSerializer(serializers.ModelSerializer):
    ingredientes = IngredienteRecetaSerializer(many=True, required=False)
    categoria_nutricional = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Receta
        fields = [
            "id",
            "hogar",
            "nombre",
            "descripcion",
            "tiempo_preparacion",
            "instrucciones",
            "categoria_nutricional",  # 🆕 campo nuevo
            "ingredientes",
            "imagen",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["hogar"]

    # 🔹 Crear receta junto con ingredientes
    def create(self, validated_data):
        ingredientes_data = validated_data.pop("ingredientes", [])
        receta = Receta.objects.create(**validated_data)

        for item in ingredientes_data:
            IngredienteReceta.objects.create(receta=receta, **item)

        return receta

    # 🔹 Actualizar receta junto con ingredientes
    def update(self, instance, validated_data):
        ingredientes_data = validated_data.pop("ingredientes", [])

        # Actualizar campos de receta
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Eliminar los ingredientes anteriores y recrear
        instance.ingredientes.all().delete()
        for item in ingredientes_data:
            IngredienteReceta.objects.create(receta=instance, **item)

        return instance


class PlanSemanalSerializer(serializers.ModelSerializer):
    receta = RecetaSerializer(read_only=True)
    receta_id = serializers.PrimaryKeyRelatedField(
        queryset=Receta.objects.all(), source='receta', write_only=True
    )

    class Meta:
        model = PlanSemanal
        fields = [
            'id',
            'hogar',
            'dia',
            'tipo_comida',
            'receta',
            'receta_id',
            'creado_por',
            'creado_en',
        ]
        read_only_fields = ['hogar', 'creado_por', 'creado_en']
