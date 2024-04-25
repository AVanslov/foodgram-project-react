from djoser.serializers import UserSerializer
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from .fields import Hex2NameColor
from recipes.models import (
    Follow,
    Favorite,
    ShoppingCart,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    User,
)

MIN_INGREDIENTS_AMOUNT = 1


class AuthorSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['is_subscribed', *UserSerializer.Meta.fields]

    def get_is_subscribed(self, user):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user,
                following=user
            ).exists()
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


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = AuthorSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
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
            'text',
            'cooking_time',
            'image',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, recipe):
        request = self.context['request']
        return bool(
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=recipe.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        return bool(
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe.id
            ).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = AuthorSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientWriteSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    text = serializers.CharField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'image',
        )

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        ingredients = data.get('recipe_ingredients')
        if not ingredients:
            raise ValidationError('Список ингридиентов не может быть пустым.')

        check_unique_id = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            check_unique_id.append(ingredient_id)
        if len(check_unique_id) != len(set(check_unique_id)):
            raise ValidationError('Ингридиенты должны быть уникальными.')

        tags_data = data.get('tags')
        if not tags_data:
            raise ValidationError('Список тегов не может быть пустым.')
        if len(tags_data) != len(set(tags_data)):
            raise ValidationError('Теги должны быть уникальными.')
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Изображение обязательно должно быть.')
        return value

    def create_ingredients(self, ingredients, recipe):
        return RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags_data)

        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe_ingredients = instance.recipe_ingredients.all()
        recipe_ingredients.delete()

        self.create_ingredients(ingredients_data, instance)

        return super().update(instance, validated_data)


class RecipesWriteFromFollowingSerializer(RecipeWriteSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipesReadFromFollowingSerializer(RecipeReadSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(AuthorSerializer):
    username = serializers.CharField(
        source='following.username',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='following.id',
        read_only=True
    )
    first_name = serializers.CharField(
        source='following.first_name',
        read_only=True
    )
    last_name = serializers.CharField(
        source='following.last_name',
        read_only=True
    )
    email = serializers.CharField(
        source='following.email',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='following.recipes.count',
        read_only=True
    )

    class Meta:
        model = Follow
        # fields = ['recipes', 'recipes_count', *AuthorSerializer.Meta.fields]
        fields = (
            'username',
            'id',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count',
            # *AuthorSerializer.Meta.fields
        )
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Follow.objects.all(),
        #         fields=['user', 'following']
        #     )
        # ]

    def get_is_subscribed(self, follow):
        return Follow.objects.filter(user=self.context['request'].user, following=follow.following).exists()

    def validate(self, data):
        request = self.context['request']
        following_id = data.get('id')

        if request.method == 'POST' and Follow.objects.filter(user=request.user, following=following_id).exists():
            raise ValidationError('Вы уже подписаны на этого автора.')
        if request.method != 'POST':
            return data
        if request.user.id != following_id:
            return data
        raise ValidationError('Вы не можете подписаться на себя.')

    def get_recipes(self, follow):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        result = follow.following.recipes.all()
        if recipes_limit is None:
            result
        else:
            result = result[:int(recipes_limit)]
        return RecipesReadFromFollowingSerializer(result, many=True).data
