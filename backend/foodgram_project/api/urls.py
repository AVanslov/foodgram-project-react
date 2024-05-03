from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    FollowViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

router = DefaultRouter()

router.register('ingredients', IngredientViewSet)

router.register('tags', TagViewSet)

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
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
