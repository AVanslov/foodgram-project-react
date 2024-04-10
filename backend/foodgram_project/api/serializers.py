import webcolors

from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from .serializers import UserSerializer

from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import User


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
        fields = ['is_subscribed', *UserSerializer.Meta.fields]

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.followers.filter(following=obj).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='favorites.id',
        read_only=True
    )
    name = serializers.CharField(
        source='favorites.name',
        read_only=True
    )
    image = Base64ImageField(
        source='favorites.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='favorites.cooking_time',
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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = IngredientSerializer()
    name = serializers.CharField(required=False)
    measurement_unit = serializers.IntegerField(required=False)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'The amount of ingredients must be greater than 0.'
                )
            RecipeIngredient.objects.bulk_create(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        instance.tags.set(tags)
        Recipe.objects.filter(pk=instance.pk).update(**validated_data)
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'The amount of ingredients must be greater than 0.'
                )
            RecipeIngredient.objects.bulk_create(
                ingredient=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount'],
            )
        return instance.refresh_from_db()

    def get_is_favorited(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.purchases.filter(recipe=obj).exists()


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
        source='authors.id', read_only=True
    )
    username = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    first_name = serializers.CharField(
        source='authors.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='authors.last_name', read_only=True
    )
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='authors.recipes.count', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['is_subscribed', *UserSerializer.Meta.fields]

    def get_is_subscribed(self, obj):
        return obj.user.authors.filter(following=obj.following).exists()

    def get_recipes(self, user):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is None:
            result = user.following.recipes.all()
        else:
            recipes_limit = int(request.query_params.get('recipes_limit'))
            result = user.following.recipes.all()[:recipes_limit]
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
        source='purchases.id',
        read_only=True
    )
    name = serializers.CharField(
        source='purchases.name',
        read_only=True
    )
    image = Base64ImageField(
        source='purchases.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='purchases.cooking_time',
        read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
