from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ApiFavorite,
    ApiShoppingCart,
    UserViewSet,
    FollowViewSet,
    get_list,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

router = DefaultRouter()

router.register('ingredients', IngredientViewSet)

router.register('tags', TagViewSet)

router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    FollowViewSet,
    basename='subscribe',
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
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
    path(
        r'recipes/<int:recipe_id>/shopping_cart',
        ApiShoppingCart.as_view()
    ),
    path(
        r'recipes/<int:recipe_id>/favorite',
        ApiFavorite.as_view()
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
