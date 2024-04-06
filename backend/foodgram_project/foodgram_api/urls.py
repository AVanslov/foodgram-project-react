from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet,
    FollowViewSet,
    get_list,
    IngredientViewSet,
    RecipeViewSet,
    ShoppingCartViewSet,
    TagViewSet,
)

router_v1 = DefaultRouter()

router_v1.register(r'ingredients', IngredientViewSet)
router_v1.register(
    r'ingredients/(?P<ingredient_id>\d+)/',
    IngredientViewSet,
    basename='ingredients',
)
router_v1.register(r'tags', TagViewSet)
router_v1.register(
    r'tags/(?P<tag_id>\d+)/',
    TagViewSet,
    basename='tags',
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite',
)
router_v1.register(
    r'favorites',
    FavoriteViewSet,
    basename='favorite_list',
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart',
)
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/',
    RecipeViewSet,
    basename='recipes',
)
router_v1.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowViewSet,
    basename="subscribe",
)
router_v1.register(
    r'users/subscriptions', FollowViewSet, basename='subscriptions'
)


urlpatterns = [
    path(
        r'recipes/download_shopping_cart/',
        get_list,
        name='download_shopping_cart',
    ),
    path('', include(router_v1.urls)),
]
