from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from isdigit import IsDigit

from .fields import Hex2NameColor
from recipes.models import (
    Favorite,
    Follow,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Ingredient,
    Tag,
    User,
)

digits = IsDigit()


class AuthorSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['is_subscribed', *UserSerializer.Meta.fields]

    def get_is_subscribed(self, user):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and request.user.followers.filter(following=user).exists()
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
        return (
            request
            and request.user.is_authenticated
            and request.user.favorite.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        return (
            request
            and request.user.is_authenticated
            and request.user.shoppingcart.filter(recipe=recipe).exists()
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

        check_unique_id = [ingredient.get('id') for ingredient in ingredients]

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
            raise serializers.ValidationError(
                'Изображение обязательно должно быть.'
            )
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
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
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
    id = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.IntegerField(
        read_only=True
    )

    class Meta(RecipeReadSerializer.Meta):
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
        source='following.recipes.count',
        read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            'user',
            'following',
            'recipes',
            'recipes_count',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        additional_values = AuthorSerializer(
            instance.user,
            context={'request': self.context.get('request')}
        ).data

        for key, value in additional_values.items():
            representation[key] = value

        del representation['user']
        del representation['following']

        return representation

    def validate(self, data):
        request = self.context['request']
        following = data.get('following')
        if Follow.objects.filter(
            user=request.user,
            following=following.id
        ).exists():
            raise ValidationError('Вы уже подписаны на этого автора.')
        if request.user.id == following.id:
            raise ValidationError('Вы не можете подписаться на себя.')
        return data

    def get_recipes(self, follow):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        result = follow.following.recipes.all()
        if digits.is_digit(str(recipes_limit)):
            result = result[:int(recipes_limit)]
        return RecipesReadFromFollowingSerializer(result, many=True).data


class BaseShoppingCartAndFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'user',
            'recipe',
        )

    def to_representation(self, instance):
        return RecipesReadFromFollowingSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        request = self.context['request']
        recipe_id = data.get('id')

        if self.Meta.model.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок')

        return data


class ShoppingCartSerializer(BaseShoppingCartAndFavoriteSerializer):

    class Meta(BaseShoppingCartAndFavoriteSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(BaseShoppingCartAndFavoriteSerializer):

    class Meta(BaseShoppingCartAndFavoriteSerializer.Meta):
        model = Favorite
