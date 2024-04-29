from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ApiFavorite,
    ApiShoppingCart,
    # ShoppingCartViewSet,
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

# router.register(
#     r'recipes/?P<recipe_id>\d+/shopping_cart',
#     ShoppingCartViewSet,
#     basename='shoppingcarts'
# )

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
    'users/subscriptions', FollowViewSet, basename='subscriptions'
)

router.register('users', UserViewSet)

urlpatterns = [
    # path('users/subscriptions', subscribe_list),
    # path('users/(<int:user_id>)/subscribe', subscribe),
    path(
        'recipes/download_shopping_cart/',
        get_list,
        name='download_shopping_cart',
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart',
        ApiShoppingCart.as_view()
    ),
    path(
        'recipes/<int:recipe_id>/favorite',
        ApiFavorite.as_view()
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
