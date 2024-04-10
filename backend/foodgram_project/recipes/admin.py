from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    User,
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    empty_value_display = '-empty-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
        'recipes_count',
    )
    list_filter = ('measurement_unit',)
    empty_value_display = '-empty-'

    @admin.display(empty_value=None)
    def recipes_count(self, ingredient):
        return ingredient.recipes.all().count()


class CookongTimeListFilter(admin.SimpleListFilter):
    title = ('Время приготовления')
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):

        qs = model_admin.get_queryset(request)
        if qs.filter(
            cooking_time__range=(0, 10),
        ).exists():
            yield ('быстрые', ('быстрее 10 минут'))
        if qs.filter(
            cooking_time__range=(10, 30),
        ).exists():
            yield ('средние', ('быстрее 30 минут'))
        else:
            yield ('долгие', ('более 30 минут'))


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'followers',
        'cooking_time',
        'image',
        'tags',
        'ingredients'
    )
    list_filter = [CookongTimeListFilter]
    empty_value_display = '-empty-'

    @admin.display(description='Подписчики', empty_value=None)
    def followers(self, recipe):
        return recipe.favorites.all().count()

    @admin.display(description='Теги', empty_value=None)
    def tags(self, recipe):
        for tag in recipe.recipe_tags.all():
            return mark_safe(tag.name)[:50] + '<br>'

    @admin.display(description='Ингредиенты', empty_value=None)
    def ingredients(self, recipe):
        for ingredient in recipe.recipe_ingredients.all():
            return (
                mark_safe(ingredient.name)[:50],
                mark_safe(ingredient.measurement_unit),
                mark_safe(ingredient.amount) + '<br>'
            )



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    empty_value_display = '-empty-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'amount'
    )
    empty_value_display = '-empty-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    empty_value_display = '-empty-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following'
    )
    empty_value_display = '-empty-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    empty_value_display = '-empty-'
