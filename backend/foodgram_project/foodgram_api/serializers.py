from django.contrib.auth import get_user_model
import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction
from users.serializers import UserSerializer
import webcolors

from .models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class AuthorSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.follower.filter(following=obj).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='favorite_recipe.id',
        read_only=True
    )
    name = serializers.CharField(
        source='favorite_recipe.name',
        read_only=True
    )
    image = Base64ImageField(
        source='favorite_recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='favorite_recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'

    def to_internal_value(self, data):
        return Tag.objects.get(id=data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

    def to_internal_value(self, data):
        return Ingredient.objects.get(id=data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = IngredientSerializer()
    name = serializers.CharField(required=False)
    measurement_unit = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'quantity',
        )

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['quantity'] = instance.quantity
        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
    )
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            if ingredient['quantity'] <= 0:
                raise serializers.ValidationError(
                    'The quantity of ingredients must be greater than 0.'
                )
            RecipeIngredient.objects.create(
                ingredient=ingredient['id'],
                recipe=recipe,
                quantity=ingredient['quantity'],
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        instance.tags.set(tags)
        Recipe.objects.filter(pk=instance.pk).update(**validated_data)
        for ingredient in ingredients:
            if ingredient['quantity'] <= 0:
                raise serializers.ValidationError(
                    'The quantity of ingredients must be greater than 0.'
                )
            RecipeIngredient.objects.create(
                ingredient=ingredient['id'],
                recipe=instance,
                quantity=ingredient['quantity'],
            )
        instance.refresh_from_db()
        return instance

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.favorite_recipes.filter(favorite_recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.in_cart.filter(recipe_in_cart=obj).exists()


class RecipiesFromFollowingSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(UserSerializer):
    email = serializers.EmailField(source='following.email', read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='following.id', read_only=True
    )
    username = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    first_name = serializers.CharField(
        source='following.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='following.last_name', read_only=True
    )
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='following.recipes.count', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_is_subscribed(self, obj):
        return obj.user.follower.filter(following=obj.following).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is None:
            result = obj.following.recipes.all()
        else:
            recipes_limit = int(request.query_params.get('recipes_limit'))
            result = obj.following.recipes.all()[:recipes_limit]
        return RecipiesFromFollowingSerializer(result, many=True).data

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        current_user = str(request.user.id)
        following = request.parser_context['kwargs']['user_id']
        if current_user != following:
            return data
        raise ValidationError('You cannot follow yourself')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe_in_cart.id', read_only=True
    )
    name = serializers.CharField(source='recipe_in_cart.name', read_only=True)
    image = Base64ImageField(source='recipe_in_cart.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe_in_cart.cooking_time', read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
