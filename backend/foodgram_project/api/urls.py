from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ApiFavorite,
    ApiShoppingCart,
    FollowViewSet,
    get_list,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
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
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    'users/subscriptions', FollowViewSet, basename='subscribtions'
)

router.register('users', UserViewSet)

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ApiShoppingCart.as_view(),
        name='shoppingcarts'
    ),
    path(
        'recipes/download_shopping_cart/',
        get_list,
        name='download_shopping_cart',
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        ApiFavorite.as_view(),
        name='favorites'
    ),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
