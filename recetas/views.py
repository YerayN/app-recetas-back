from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from .models import Receta, Ingrediente, Unidad, PlanSemanal, IngredienteReceta
from .serializers import RecetaSerializer, IngredienteSerializer, UnidadSerializer, PlanSemanalSerializer, ListaCompraCategoriaSerializer
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import Prefetch


# ------------------- VISTAS CRUD PRINCIPALES -------------------

class UnidadViewSet(viewsets.ModelViewSet):
    """CRUD completo para Unidades"""
    queryset = Unidad.objects.all()
    serializer_class = UnidadSerializer
    permission_classes = [permissions.IsAuthenticated]


class IngredienteViewSet(viewsets.ModelViewSet):
    """CRUD completo para Ingredientes"""
    queryset = Ingrediente.objects.all()
    serializer_class = IngredienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre"]


class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "descripcion"]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Receta.objects.none()

        perfil = getattr(user, "perfil", None)
        if not perfil or not getattr(perfil, "hogar", None):
            print("⚠️ Usuario sin perfil o sin hogar asociado:", user)
            return Receta.objects.none()

        print("✅ Devolviendo recetas del hogar:", perfil.hogar)
        return Receta.objects.filter(hogar=perfil.hogar).order_by("-creado_en")

    def perform_create(self, serializer):
        user = self.request.user
        perfil = getattr(user, "perfil", None)
        if not perfil or not perfil.hogar:
            raise ValueError("El usuario no pertenece a ningún hogar válido.")
        serializer.save(hogar=perfil.hogar)


class PlanSemanalViewSet(viewsets.ModelViewSet):
    """CRUD para el Plan Semanal, filtrado por hogar del usuario"""
    queryset = PlanSemanal.objects.all()
    serializer_class = PlanSemanalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return PlanSemanal.objects.none()

        perfil = getattr(user, "perfil", None)
        if perfil is None or perfil.hogar is None:
            return PlanSemanal.objects.none()

        return (
            PlanSemanal.objects.filter(hogar=perfil.hogar)
            .select_related("receta")
            .order_by("dia")
        )

    def perform_create(self, serializer):
        """Asigna hogar y comensales por defecto al crear un plan."""
        user = self.request.user
        perfil = getattr(user, "perfil", None)

        if perfil is None or perfil.hogar is None:
            raise ValueError("El usuario no pertenece a ningún hogar válido.")

        # 🔹 Si no se especifica 'comensales', usar el valor por defecto del hogar
        hogar = perfil.hogar
        comensales_default = getattr(hogar, "comensales_default", 2)

        serializer.save(
            hogar=hogar,
            creado_por=user,
            comensales=serializer.validated_data.get("comensales", comensales_default)
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Permite actualizar parcialmente (PATCH) el campo comensales.
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------- AUTENTICACIÓN -------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Registro de usuarios con creación automática de hogar y perfil."""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Faltan campos obligatorios."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "El usuario ya existe."},
            status=status.HTTP_400_BAD_REQUEST
        )

    User.objects.create_user(username=username, password=password)
    return Response(
        {"message": "Usuario creado correctamente."},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login API para frontend.
    Devuelve el token CSRF en el response header.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Faltan credenciales'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        # ✅ Generar el token CSRF y devolverlo en el header
        csrf_token = get_token(request)
        
        response = Response(
            {'message': 'Login correcto', 'username': username},
            status=status.HTTP_200_OK
        )
        
        # Añadir el token en un header personalizado que el frontend pueda leer
        response['X-CSRFToken'] = csrf_token
        
        return response
    else:
        return Response(
            {'error': 'Usuario o contraseña incorrectos'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """Logout API — cierra sesión."""
    logout(request)
    return Response(
        {'message': 'Logout correcto'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_cookie_view(request):
    """
    Endpoint para obtener el token CSRF.
    Lo devuelve en el response header Y en el body.
    """
    csrf_token = get_token(request)
    
    response = Response(
        {"csrfToken": csrf_token},
        status=status.HTTP_200_OK
    )
    
    # Enviar también en el header para que sea más fácil de leer
    response['X-CSRFToken'] = csrf_token
    
    return response


def csrf_token_view(request):
    """
    Devuelve el token CSRF como JSON.
    Esto permite que el frontend (Vercel) lo obtenga antes de hacer login.
    """
    return JsonResponse({"csrfToken": get_token(request)})



@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def lista_compra(request):
    """
    Devuelve la lista de la compra del hogar del usuario autenticado,
    agrupada por categoría de supermercado y con cantidades ajustadas
    por el número de comensales de cada entrada del plan semanal.
    """

    user = request.user
    perfil = getattr(user, "perfil", None)
    if perfil is None or perfil.hogar is None:
        return Response([], status=status.HTTP_200_OK)

    hogar = perfil.hogar

    # Prefetch agresivo para minimizar consultas:
    planes = (
        PlanSemanal.objects
        .filter(hogar=hogar)
        .select_related("receta")
        .prefetch_related(
            Prefetch(
                "receta__ingredientes",
                queryset=(
                    ingredientes.objects
                    .select_related("ingrediente", "unidad")
                )
            )
        )
    )

    # Mapa clave->label de categorías (choices)
    categorias_dict = dict(Ingrediente.CATEGORIAS_CHOICES)

    # Estructura intermedia:
    # { categoria_key: { (ingrediente_id, unidad_id): { ...acumulado... } } }
    agrupado = defaultdict(lambda: {})

    for plan in planes:
        comensales = plan.comensales or 1
        receta = plan.receta

        for ingrec in receta.ingredientes.all():
            ingrediente = ingrec.ingrediente
            unidad = ingrec.unidad  # puede ser None
            cantidad_base = ingrec.cantidad or 0.0
            cantidad_total = (cantidad_base or 0.0) * comensales

            cat_key = ingrediente.categoria or "otros"
            cat_label = categorias_dict.get(cat_key, "Otros")

            unidad_id = unidad.id if unidad else None
            unidad_nombre = (unidad.nombre if unidad else None)
            unidad_abrev = (unidad.abreviatura if unidad else None)

            # Clave para fusionar iguales (mismo ingrediente + misma unidad)
            fusion_key = (ingrediente.id, unidad_id)

            if fusion_key not in agrupado[cat_key]:
                agrupado[cat_key][fusion_key] = {
                    "ingrediente_id": ingrediente.id,
                    "ingrediente_nombre": ingrediente.nombre,
                    "unidad": {
                        "id": unidad_id,
                        "nombre": unidad_nombre,
                        "abreviatura": unidad_abrev,
                    } if unidad_id is not None else None,
                    "cantidad_total": 0.0,
                    "detalles": [],
                    "categoria_label": cat_label,  # guardamos para no mirar luego
                }

            # Acumular
            agrupado[cat_key][fusion_key]["cantidad_total"] += cantidad_total
            agrupado[cat_key][fusion_key]["detalles"].append({
                "receta_id": receta.id,
                "receta_nombre": receta.nombre,
                "cantidad_base": cantidad_base,
                "comensales": comensales,
                "cantidad_total": cantidad_total,
            })

    # Transformar a lista serializable
    salida = []
    for cat_key, items_map in agrupado.items():
        items_list = list(items_map.values())
        # Ordenar por nombre ingrediente
        items_list.sort(key=lambda x: x["ingrediente_nombre"].lower())
        salida.append({
            "categoria_key": cat_key,
            "categoria_label": (items_list[0]["categoria_label"] if items_list else dict(Ingrediente.CATEGORIAS_CHOICES).get(cat_key, "Otros")),
            "items": items_list,
        })

    # Orden de categorías por label
    salida.sort(key=lambda c: c["categoria_label"].lower())

    serializer = ListaCompraCategoriaSerializer(salida, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
