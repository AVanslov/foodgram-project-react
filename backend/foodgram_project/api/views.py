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
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.response import Response

from converters import create_report_about_ingredient
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
    Favorite, #  найти применение
    ShoppingCart, # найти применение
    User
)
from .serializers import (
    FavoriteAndShoppingCartSerializer,
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
    lookup_field = "username"


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


# разделить безобпасные и небезопасные методы
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend, RecipeFilterBackend]
    filter_class = RecipeFilter


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        current_user = self.request.user
        following = get_object_or_404(
            User,
            id=self.kwargs['user_id'],
        )
        return serializer.save(
            user=current_user,
            following=following,
        )

    @action(
        detail=False,
        methods=['DELETE'],
    )
    def delete(self, request, user_id=None):
        get_object_or_404(
            Follow, user=request.user
        ).filter(
            following__id=user_id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteAndShoppingCartSerializer

    def get_queryset(self):
        return self.request.user.recipes.filter(is_favorite=True)

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            recipe__id=self.kwargs['recipe_id'],
            is_favorite=True,
        )

    @action(
        detail=False,
        methods=['DELETE'],
    )
    def delete(self, request, recipe_id=None):
        get_object_or_404(
            UserRecipeModel,
            user=request.user,
            recipe__id=recipe_id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteAndShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user
        cart = user.purchases.filter(is_in_shopping_cart=True)
        result = {}
        for recipe in cart:
            ingredients = recipe.recipe.recipeingredient_set.all()
            for ingredient in ingredients:
                result += ingredient.aggregate(Sum('ingredient__amount'))
        return result

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            recipe__id=self.kwargs['recipe_id'],
            is_in_shopping_cart=True
        )

    @action(
        detail=False,
        methods=['DELETE'],
    )
    def delete(self, request, recipe_id=None):
        get_object_or_404(
            UserRecipeModel,
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
