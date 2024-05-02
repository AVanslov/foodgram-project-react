from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

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
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipesReadFromFollowingSerializer,
    TagSerializer,
)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = AuthorSerializer
    # lookup_field = 'user_id'
    # lookup_url_kwarg = 'user_id'

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_pagination_class(self):
        if self.action in ['create', 'list']:
            return FollowResultsSetPagination
        return ResultsSetPagination

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=False, methods=['POST'], url_path=r'(?P<user_id>\d+)/subscribe')
    def create_subscriber(self, request, user_id=None):
        additional_values = {
            'user': self.request.user.id,
            'following': user_id
        }
        for key, value in additional_values.items():
            request.data[key] = value
        get_object_or_404(User, id=user_id)
        serializer = FollowSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            # headers=headers
        )
    # def perform_create(self, serializer):
    #     return serializer.save(
    #         user=self.request.user,
    #         following=get_object_or_404(User, id=self.kwargs['user_id'])
    #     )

    @action(detail=False, methods=['DELETE'], url_path=r'(?P<user_id>\d+)/subscribe')
    def delete(self, request, user_id=None):
        follow = Follow.objects.filter(
            user=request.user,
            following=get_object_or_404(User, id=user_id)
        )
        if not follow.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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

    # def create(self, request, *args, **kwargs):
    #     data = {
    #         'user': self.request.user.id,
    #         'following': self.kwargs['user_id']
    #     }
    #     get_object_or_404(User, id=self.kwargs['user_id'])
    #     serializer = self.get_serializer(data=data)
    #     serializer.is_valid(raise_exception=True)
        # if Follow.objects.filter(
        #     user=self.request.user,
        #     following__id=self.kwargs['user_id']
        # ).exists():
        #     return Response(
        #         serializer.errors,
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        # if self.request.user == get_object_or_404(
        #     User,
        #     id=self.kwargs['user_id']
        # ):
        #     return Response(
        #         serializer.errors,
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # serializer.save()
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(
        #     serializer.data,
        #     status=status.HTTP_201_CREATED,
        #     headers=headers
        # )

    # def perform_create(self, serializer):
    #     return serializer.save(
    #         user=self.request.user,
    #         following=get_object_or_404(User, id=self.kwargs['user_id'])
    #     )

    # @action(detail=False, methods=['DELETE'])
    # def delete(self, request, user_id=None):
    #     follow = Follow.objects.filter(
    #         user=request.user,
    #         following=get_object_or_404(User, id=user_id)
    #     )
    #     if not follow.exists():
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #     follow.delete()

    #     return Response(status=status.HTTP_204_NO_CONTENT)


class ApiFavorite(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, recipe_id):
        serializer = RecipesReadFromFollowingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Favorite.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            recipe_obj = Recipe.objects.get(id=recipe_id)
        except Exception:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe = Favorite.objects.create(
            user=request.user,
            recipe=recipe_obj
        )
        recipe.save()
        return Response(
            RecipesReadFromFollowingSerializer(recipe_obj).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not Favorite.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApiShoppingCart(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, recipe_id):
        serializer = RecipesReadFromFollowingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if not self.request.user.is_authenticated:
                return Response(
                    serializer.errors,
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe__id=recipe_id
            ).exists():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                recipe_obj = Recipe.objects.get(id=recipe_id)
            except Exception:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe = ShoppingCart.objects.create(
                user=request.user,
                recipe=recipe_obj
            )
            recipe.save()
            return Response(
                RecipesReadFromFollowingSerializer(recipe_obj).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_list(request):
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
