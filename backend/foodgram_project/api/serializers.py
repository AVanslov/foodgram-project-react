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
    id = serializers.IntegerField(source='ingredient.pk')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


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
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True
    )
    image = Base64ImageField(required=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False
    )

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
        data['author'] = self.context['request'].user

        tags = self.initial_data.get('tags')
        if not isinstance(tags, list):
            raise serializers.ValidationError('tags must be list')
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError('No tag')
        data['tags'] = tags

        ingredients = self.initial_data.get('ingredients')
        if not isinstance(ingredients, list):
            raise serializers.ValidationError('ingredients must be list')
        valid_ingredients = []
        ingredient_objects = Ingredient.objects.filter(
            id__in=[ingredient.get('id') for ingredient in ingredients]
        )
        if len(ingredient_objects) != len(ingredients):
            raise serializers.ValidationError('invalid ingredient')
        for ing_obj, ingredient in zip(ingredient_objects, ingredients):
            amount = int(ingredient.get('amount'))
            if amount < 1:
                raise serializers.ValidationError('invalid amount')
            valid_ingredients.append(
                {'ingredient': ing_obj, 'amount': amount}
            )
        data['ingredients'] = valid_ingredients
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=ingredient['ingredient'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        if tags:
            instance.tags.clear()
            instance.tags.set(tags)

        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            instance.ingredients.clear()
            RecipeIngredient.objects.bulk_create([
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
                for ingredient in ingredients
            ])
        instance.save()
        return instance


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
