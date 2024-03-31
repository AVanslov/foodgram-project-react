from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Recipe,
    User,
)
from .serializers import RecipeSerializer, UserSerializer


@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.all()
    serializer = UserSerializer(user, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def recipe_list(request):
    if request.method == 'POST':
        serializer = RecipeSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = Recipe.objects.all()
    serializer = RecipeSerializer(user, many=True)
    return Response(serializer.data)
