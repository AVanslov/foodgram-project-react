from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html

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


class OnlyWithFollowersOrFollowingsListFilter(admin.SimpleListFilter):
    title = ('Фильтр по наличию подписиков и подписок')

    def lookups(self, request, model_admin):

        qs = model_admin.get_queryset(request)
        if qs.filter(
            follower__count=0,
        ).exists():
            yield ('нет подписчиков', ('Число подписчиков 0'))
        if qs.filter(
            following__count=0,
        ).exists():
            yield ('нет подписок', ('Число подписок 0'))
        else:
            yield ('все', ('все'))


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'recipes_count',
        'followers',
        'following',
    )
    list_filter = [OnlyWithFollowersOrFollowingsListFilter]
    empty_value_display = '-empty-'

    @admin.display(empty_value=None)
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписчики', empty_value=None)
    def followers(self, user):
        return user.followers.count()

    @admin.display(description='Подписки', empty_value=None)
    def following(self, user):
        return user.author.count()


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
        return ingredient.recipes.count()


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
        'in_favorite_count',
        'cooking_time',
        'image',
        'tags',
        'ingredients'
    )
    list_filter = [CookongTimeListFilter]
    empty_value_display = '-empty-'

    @admin.display(description='Подписчики', empty_value=None)
    def in_favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги', empty_value=None)
    def tags(self, recipe):
        return mark_safe(
            '<br>'.join(
                (tag.name)[:50] for tag in recipe.recipe_tags.all()
            )
        )

    def image(self, recipe):
        return mark_safe(
            f'<img scr="{recipe.image.url}" style="max-width:200px; max-height:200px"/>'
        )

    @admin.display(description='Ингредиенты', empty_value=None)
    def ingredients(self, recipe):
        return mark_safe(
            '<br>'.join(
                (ingredient.name)[:50],
                ingredient.measurement_unit,
                ingredient.amount
            ) for ingredient in recipe.recipe_ingredients.all()
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
