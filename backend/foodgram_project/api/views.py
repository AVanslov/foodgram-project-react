from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from djoser.views import UserViewSet
from rest_framework import generics
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .converters import create_report_about_ingredient
from .filters import (
    IngredientFilter,
    RecipeFilter,
    RecipeFilterBackend,
)
from recipes.models import (
    Follow,
    Ingredient,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart,
    User
)
from .serializers import (
    RecipiesFromFollowingSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    UserSerializer,
)


class UserViewSet(UserViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend, RecipeFilterBackend]
    filter_class = RecipeFilter
    lookup_field = 'recipe_id'

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return RecipeWriteSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return self.request.user.authors.all()

    def perform_create(self, serializer):
        current_user = self.request.user
        return serializer.save(
            user=current_user
        )

    @action(detail=False, methods=['DELETE'])
    def delete(self, request, user_id=None):
        get_object_or_404(
            Follow,
            user=request.user,
            following__id=user_id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ApiFavorite(APIView):

    def post(self, request):
        serializer = RecipiesFromFollowingSerializer(data=request.data)
        if serializer.is_valid():
            recipe = Favorite.objects.create(
                user=self.request.user,
                recipe__id=self.kwargs['recipe_id']
            )
            recipe.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe__id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApiShoppingCart(APIView):

    def post(self, request):
        serializer = RecipiesFromFollowingSerializer(data=request.data)
        if serializer.is_valid():
            recipe = ShoppingCart.objects.create(
                user=self.request.user,
                recipe__id=self.kwargs['recipe_id']
            )
            recipe.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe__id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_list(request):
    user = request.user
    ingredients_data = user.purchases.ingredients.values('name').annotate(
        ingredient_amount=Sum('ingredient__amount')
    ).order_by('ingredient__name')
    ingredients_list = [
        create_report_about_ingredient(ingredient_number, ingredient)
        for ingredient_number, ingredient
        in enumerate(ingredients_data, start=1)
    ]

    return FileResponse(
        ingredients_list,
        as_attachment=True,
        filename='list.txt'
    )
