from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import permission_classes
from rest_framework import (
    filters,
    permissions,
    status,
    viewsets,
)
from djoser.views import UserViewSet
from rest_framework.decorators import (
    action,
    api_view,
)
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .paginator import (
    FollowResultsSetPagination,
    ResultsSetPagination,
)
from .converters import create_report_about_ingredient
from .filters import (
    # AuthorAndTagFilter,
    IngredientFilter,
    RecipeFilter,
)
from . permissions import (
    IsRecipeAuthorOrReadOnly,
)
from recipes.models import (
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    Favorite,
    ShoppingCart,
    User
)
from .serializers import (
    FollowSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipesReadFromFollowingSerializer,
    RecipesWriteFromFollowingSerializer,
    TagSerializer,
    AuthorSerializer,
)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()


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

    permission_classes = (IsAuthenticatedOrReadOnly, IsRecipeAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return RecipeWriteSerializer


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        lookup_field = self.kwargs['user_id']
        return get_object_or_404(Follow, user=self.request.user, following__pk=lookup_field)

    def get_pagination_class(self):
        if self.action in ['create', 'list']:
            return FollowResultsSetPagination
        return ResultsSetPagination

    def get_queryset(self):
        return self.request.user.followers.all().order_by('following__username')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Follow.objects.filter(
            user=self.request.user,
            following__id=self.kwargs['user_id']
        ).exists():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if self.request.user == get_object_or_404(User, id=self.kwargs['user_id']):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save(
            user=self.request.user,
            following=get_object_or_404(User, id=self.kwargs['user_id'])
        )

    @action(detail=False, methods=['DELETE'])
    def delete(self, request, user_id=None):
        follow = Follow.objects.filter(
            user=request.user,
            following=get_object_or_404(User, id=user_id)
        )
        if not follow.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ApiFavorite(APIView):

    def post(self, request):
        serializer = RecipesReadFromFollowingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            recipe = Favorite.objects.create(
                user=self.request.user,
                recipe=Recipe.objects.get(id=self.kwargs['recipe_id'])
            )
            recipe.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):
        # if not request.user.IsAuthenticated:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)
        Favorite.objects.get(
            user=request.user,
            recipe=Recipe.objects.get(id=recipe_id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApiShoppingCart(APIView):

    # def get_object(self):
    #     lookup_field = self.kwargs['recipe_id']
    #     return get_object_or_404(ShoppingCart, user=self.request.user, recipe__pk=lookup_field)

    def post(self, request):
        serializer = RecipesReadFromFollowingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # if not request.user.IsAuthenticated:
            #     return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
            # elif ShoppingCart.objects.filter(user=self.request.user, recipe__id=self.kwargs['recipe_id']).exists():
            #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # elif not Recipe.objects.get(id=self.kwargs['recipe_id']):
            #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            recipe = ShoppingCart.objects.create(
                user=self.request.user.id,
                recipe=Recipe.objects.get(id=self.kwargs['recipe_id'])
                # recipe=get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
            )
            recipe.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, recipe_id):

        # if self.request.user.is_anonymous:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)
        # if not ShoppingCart.objects.filter(
        #     user=request.user,
        #     recipe__id=recipe_id
        # ).exists():
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(
            user=request.user,
            recipe=Recipe.objects.get(id=recipe_id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_list(request):
    user = request.user
    ingredients_data = ShoppingCart.objects.filter(user=user).values('recipe__ingredients__name').annotate(
        ingredient_amount=Sum('recipe__recipe_ingredients__amount')
    ).order_by('recipe__ingredients__name')
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
