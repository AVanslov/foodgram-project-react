import webcolors

from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    User,
)


class AuthorSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['is_subscribed', *UserSerializer.Meta.fields]

    def get_is_subscribed(self, user):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return request.user.followers.filter(following=user).exists()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени.')
        return data


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


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
    )
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

    def get_is_favorited(self, recipe):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.shoppingcarts.filter(recipe=recipe).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
    )
    image = Base64ImageField(required=True)
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

    def validate(self, data):
        ingredients = data.pop('recipe_ingredients')
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Мера продукта должна быть больше 0.'
                )
            return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            ingredient=[ingredient['id'] for ingredient in ingredients],
            recipe=recipe,
            amount=[ingredient['amount'] for ingredient in ingredients],
        )
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance.tags.set(tags)
        Recipe.objects.filter(pk=instance.pk).update(**validated_data)
        RecipeIngredient.objects.bulk_create(
            ingredient=[ingredient['id'] for ingredient in ingredients],
            recipe=instance,
            amount=[ingredient['amount'] for ingredient in ingredients],
        )
        return serializers.ModelSerializer.update(
            self, instance, validated_data
        )


class RecipiesFromFollowingSerializer(RecipeReadSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(AuthorSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='authors.recipes.count', read_only=True
    )

    class Meta:
        model = Follow
        fields = [*AuthorSerializer.Meta.fields]

    def get_recipes(self, user):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is None:
            result = user.authors.recipes.all()
        else:
            result = user.authors.recipes.all()[:int(recipes_limit)]
        return RecipiesFromFollowingSerializer(result, many=True).data

    def validate_following(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        if str(request.user.id) != data['following']:
            return data
        raise ValidationError('Вы не можете подписаться на себя.')
