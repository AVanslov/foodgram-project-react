from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    FavoriteViewSet,
    FollowViewSet,
    get_list,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
)

router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet)

router.register(r'tags', TagViewSet)


router.register(
    r'favorites',
    FavoriteViewSet,
    basename='favorite_list',
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart',
)
router.register(r'recipes', RecipeViewSet)

router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowViewSet,
    basename="subscribe",
)
router.register(
    r'users/subscriptions', FollowViewSet, basename='subscriptions'
)

router.register('users', UserViewSet)

urlpatterns = [
    path(
        r'recipes/download_shopping_cart/',
        get_list,
        name='download_shopping_cart',
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
