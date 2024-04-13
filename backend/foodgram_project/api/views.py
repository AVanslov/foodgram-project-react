from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.response import Response

from .filters import (
    IngredientFilter,
    RecipeFilter,
    RecipeFilterBackend,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from .serializers import (
    FavoriteRecipeSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)

User = get_user_model()


from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from .serializers import UserSerializer


class CustomUserViewSet(UserViewSet):
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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
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
    serializer_class = FavoriteRecipeSerializer

    def get_queryset(self):
        return self.request.user.favorites.all()

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            recipe__id=self.kwargs['recipe_id'],
        )

    @action(
        detail=False,
        methods=['DELETE'],
    )
    def delete(self, request, recipe_id=None):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe__id=recipe_id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user
        cart = user.purchases.all()
        result = {}
        for recipe in cart:
            ingredients = recipe.recipe.ingredientinrecipe_set.all()
            for ingredient in ingredients:
                amount_in_cart = ingredient.amount
                ingredient_in_cart_id = ingredient.ingredient.id
                if ingredient_in_cart_id in result:
                    result[ingredient_in_cart_id] += amount_in_cart
                else:
                    result[ingredient_in_cart_id] = amount_in_cart

        return result

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            recipe__id=self.kwargs['recipe_id']
        )

    @action(
        detail=False,
        methods=['DELETE'],
    )
    def delete(self, request, recipe_id=None):
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe__id=recipe_id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_list(request):
    user = request.user
    cart = user.in_cart.all()
    result = {}
    for recipe in cart:
        ingredients = recipe.recipe.recipeingredient_set.all()
        for ingredient in ingredients:
            amount_in_cart = ingredient.amount
            ingredient_in_cart_name = ingredient.ingredient.name
            if ingredient_in_cart_name in result:
                result[ingredient_in_cart_name] += amount_in_cart
            else:
                result[ingredient_in_cart_name] = amount_in_cart
    ingredients_list = str(result)
    return FileResponse(
        ingredients_list,
        as_attachment=True,
        filename='list.txt'
    )
