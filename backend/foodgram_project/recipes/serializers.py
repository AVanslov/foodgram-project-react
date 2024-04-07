from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import User


class CurrentUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.follower.filter(following=obj).exists()
