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
    RecipeDetail,
    RecipeListView,
    TagViewSet,
)

router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet)

router.register(r'tags', TagViewSet)

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
    path(
        r'recipes/(?P<recipe_id>\d+)/shopping_cart',
        ApiShoppingCart.as_view()
    ),
    path(
        r'recipes/(?P<recipe_id>\d+)/favorite',
        ApiFavorite.as_view()
    ),
    path(
        r'recipes/(?P<recipe_id>\d+)',
        RecipeDetail.as_view()
    ),
    path(
        r'recipes/',
        RecipeListView.as_view()
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
