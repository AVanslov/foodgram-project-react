from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('measurement_unit',)
    empty_value_display = '-empty-'


class CookongTimeListFilter(admin.SimpleListFilter):
    title = _('Время приготовления')
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        return [
            ('быстрые', _('быстрее 10 минут')),
            ('средние', _('быстрее 30 минут')),
            ('долгие', _('более 30 минут')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'быстрые':
            return queryset.filter(
                cooking_time__lte=10
            )
        if self.value() == 'средние':
            return queryset.filter(
                cooking_time__gte=10,
                cooking_time__lte=30,
            )
        if self.value() == 'долгие':
            return queryset.filter(
                cooking_time__gte=30,
            )


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

    @admin.display(empty_value=None)
    def followers(self, obj):
        return obj.favorited_by.all().count()


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
        'quantity'
    )
    empty_value_display = '-empty-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe_in_cart'
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
        'favorite_recipe'
    )
    empty_value_display = '-empty-'
