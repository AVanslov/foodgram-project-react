from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from .serializers import UserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
