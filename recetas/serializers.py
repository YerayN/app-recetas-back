from rest_framework import serializers
from .models import Receta, Ingrediente, Unidad, IngredienteReceta, PlanSemanal


class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = ['id', 'nombre', 'abreviatura']


class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre']


class IngredienteRecetaSerializer(serializers.ModelSerializer):
    ingrediente = serializers.PrimaryKeyRelatedField(queryset=Ingrediente.objects.all())
    unidad = serializers.PrimaryKeyRelatedField(queryset=Unidad.objects.all())

    class Meta:
        model = IngredienteReceta
        fields = ['id', 'ingrediente', 'cantidad', 'unidad']


class RecetaSerializer(serializers.ModelSerializer):
    ingredientes = IngredienteSerializer(many=True, required=False)

    class Meta:
        model = Receta
        fields = [
            'id',
            'hogar',
            'nombre',
            'descripcion',
            'tiempo_preparacion',
            'instrucciones',
            'ingredientes',
            'imagen',
            'creado_en',
            'actualizado_en',
        ]
        read_only_fields = ['hogar']

    def create(self, validated_data):
        ingredientes_data = validated_data.pop('ingredientes', [])
        receta = Receta.objects.create(**validated_data)
        for ingrediente in ingredientes_data:
            IngredienteReceta.objects.create(receta=receta, **ingrediente)
        return receta

    def update(self, instance, validated_data):
        ingredientes_data = validated_data.pop('ingredientes', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.ingredientes.all().delete()
        for ingrediente in ingredientes_data:
            IngredienteReceta.objects.create(receta=instance, **ingrediente)
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
