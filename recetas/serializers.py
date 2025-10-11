from rest_framework import serializers
from .models import Receta, Ingrediente, Unidad, IngredienteReceta, PlanSemanal
from collections import defaultdict


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
    # Nombres legibles de ingrediente y unidad
    ingrediente_nombre = serializers.CharField(source="ingrediente.nombre", read_only=True)
    unidad_nombre = serializers.SerializerMethodField()

    class Meta:
        model = IngredienteReceta
        fields = [
            "id",
            "ingrediente",
            "ingrediente_nombre",
            "cantidad",
            "unidad",
            "unidad_nombre",
        ]

    def get_unidad_nombre(self, obj):
        if obj.unidad:
            if obj.unidad.abreviatura:
                return obj.unidad.abreviatura
            return obj.unidad.nombre
        return None


class RecetaSerializer(serializers.ModelSerializer):
    ingredientes = IngredienteRecetaSerializer(many=True, required=False)

    class Meta:
        model = Receta
        fields = [
            "id",
            "hogar",
            "nombre",
            "descripcion",
            "tiempo_preparacion",
            "instrucciones",
            "categoria_nutricional",
            "ingredientes",
            "imagen",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["hogar"]

    def create(self, validated_data):
        ingredientes_data = validated_data.pop("ingredientes", [])
        receta = Receta.objects.create(**validated_data)
        for item in ingredientes_data:
            IngredienteReceta.objects.create(receta=receta, **item)
        return receta

    def update(self, instance, validated_data):
        ingredientes_data = validated_data.pop("ingredientes", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.ingredientes.all().delete()
        for item in ingredientes_data:
            IngredienteReceta.objects.create(receta=instance, **item)
        return instance


class PlanSemanalSerializer(serializers.ModelSerializer):
    # lectura: receta anidada
    receta = serializers.SerializerMethodField(read_only=True)
    # escritura: id de receta
    receta_id = serializers.PrimaryKeyRelatedField(
        queryset=Receta.objects.all(), source="receta", write_only=True
    )

    class Meta:
        model = PlanSemanal
        fields = [
            "id",
            "hogar",
            "dia",
            "tipo_comida",
            "receta",       # <- anidado (read)
            "receta_id",    # <- pk para crear/editar (write)
            "comensales",   # <- MUY IMPORTANTE
        ]
        read_only_fields = ["hogar"]

    def get_receta(self, obj):
        # Devuelve lo mínimo que usas en el front; puedes usar un serializer
        return {"id": obj.receta_id, "nombre": obj.receta.nombre}

    def create(self, validated_data):
        request = self.context["request"]
        hogar = request.user.perfil.hogar
        validated_data["hogar"] = hogar
        # si no viene, por defecto el del hogar
        if "comensales" not in validated_data:
            validated_data["comensales"] = getattr(hogar, "comensales_default", 2)
        return super().create(validated_data)
    

class ListaCompraUnidadSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    nombre = serializers.CharField(allow_blank=True, allow_null=True)
    abreviatura = serializers.CharField(allow_blank=True, allow_null=True)


class ListaCompraItemSerializer(serializers.Serializer):
    ingrediente_id = serializers.IntegerField()
    ingrediente_nombre = serializers.CharField()
    unidad = ListaCompraUnidadSerializer(allow_null=True)
    cantidad_total = serializers.FloatField()
    detalles = serializers.ListField(child=serializers.DictField(), required=False)


class ListaCompraCategoriaSerializer(serializers.Serializer):
    categoria_key = serializers.CharField()
    categoria_label = serializers.CharField()
    items = ListaCompraItemSerializer(many=True)


class IngredienteRecetaDetalleSerializer(serializers.ModelSerializer):
    ingrediente_nombre = serializers.CharField(source="ingrediente.nombre", read_only=True)
    unidad_nombre = serializers.CharField(source="unidad.nombre", read_only=True)
    unidad_abreviatura = serializers.CharField(source="unidad.abreviatura", read_only=True)

    class Meta:
        model = IngredienteReceta
        fields = [
            "id",
            "ingrediente",
            "ingrediente_nombre",
            "cantidad",
            "unidad",
            "unidad_nombre",
            "unidad_abreviatura",
        ]


class RecetaDetalleSerializer(serializers.ModelSerializer):
    ingredientes = IngredienteRecetaDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = Receta
        fields = [
            "id",
            "nombre",
            "descripcion",
            "tiempo_preparacion",
            "instrucciones",
            "categoria_nutricional",
            "imagen",
            "ingredientes",  # 👈 incluye el listado completo
        ]
