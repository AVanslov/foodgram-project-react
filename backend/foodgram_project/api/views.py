from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .converters import create_full_report_about_ingredient
from .filters import (
    IngredientFilter,
    RecipeFilter,
)
from .paginator import (
    FollowResultsSetPagination,
    ResultsSetPagination,
)
from .permissions import (
    IsRecipeAuthorOrReadOnly,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    User
)
from .serializers import (
    AuthorSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_pagination_class(self):
        if self.action in ['create', 'list']:
            return FollowResultsSetPagination
        return ResultsSetPagination

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        url_path=r'(?P<user_id>\d+)/subscribe',
        permission_classes=[IsAuthenticated],
    )
    def create_subscriber(self, request, user_id=None):
        if request.method == 'DELETE':
            follow = Follow.objects.filter(
                user=request.user,
                following=get_object_or_404(User, id=user_id)
            )
            if not follow.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            follow.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        additional_values = {
            'user': self.request.user.id,
            'following': user_id
        }
        for key, value in additional_values.items():
            request.data[key] = value
        get_object_or_404(User, id=user_id)
        serializer = FollowSerializer(
            context={'request': request},
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = RecipeFilter

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsRecipeAuthorOrReadOnly
    )

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def shopping_cart_and_favorite(
        self,
        request,
        recipe_id,
        modelname,
        serializername,
    ):
        if request.method == 'DELETE':
            shopping_cart = modelname.objects.filter(
                user=request.user,
                recipe=get_object_or_404(Recipe, id=recipe_id)
            )
            if not shopping_cart.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            shopping_cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        additional_values = {
            'user': self.request.user.id,
            'recipe': recipe_id
        }
        serializer = serializername(
            context={'request': request},
            data=additional_values
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        url_path=r'(?P<recipe_id>\d+)/shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, recipe_id=None):
        return self.shopping_cart_and_favorite(
            self,
            request,
            recipe_id,
            modelname=ShoppingCart,
            serializername=ShoppingCartSerializer,
        )

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_data = ShoppingCart.objects.filter(user=user).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(
            ingredient_amount=Sum('recipe__recipe_ingredients__amount'),
        ).order_by('recipe__ingredients__name')

        return FileResponse(
            create_full_report_about_ingredient(ingredients_data),
            as_attachment=True,
            filename='list.txt'
        )

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        url_path=r'(?P<recipe_id>\d+)/favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, recipe_id=None):
        return self.shopping_cart_and_favorite(
            self,
            request,
            recipe_id,
            modelname=Favorite,
            serializername=FavoriteSerializer,
        )


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = ResultsSetPagination

    def get_pagination_class(self):
        if self.action in ['create', 'list']:
            return FollowResultsSetPagination
        return ResultsSetPagination

    def get_queryset(self):
        return self.request.user.followers.all().order_by(
            'following__username'
        )
