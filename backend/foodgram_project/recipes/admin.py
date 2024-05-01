from django.contrib import admin
from django.shortcuts import get_object_or_404
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

NAME_MAX_LENGHT = 50


class OnlyWithFollowersOrFollowingsListFilter(admin.SimpleListFilter):
    title = ('Фильтр по наличию подписиков и подписок')
    parameter_name = 'following_count'

    def lookups(self, request, model_admin):

        return [
            ('нет подписчиков', ('Число подписчиков 0')),
            ('нет подписок', ('Число подписок 0')),
            ('все', ('все'))
        ]

    def queryset(self, request, queryset):

        if self.value() == 'нет подписчиков':
            return queryset.filter(
                follower__count=0,
            )
        if self.value() == 'нет подписок':
            return queryset.filter(
                following__count=0,
            )
        if self.value() == 'все':
            return queryset.all()


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
        return user.authors.count()


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


class CookingTimeListFilter(admin.SimpleListFilter):
    title = ('Время приготовления')
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):

        return [
            ('быстрые', ('быстрее 10 минут')),
            ('средние', ('быстрее 30 минут')),
            ('долгие', ('более 30 минут'))
        ]

    def queryset(self, request, queryset):

        if self.value() == 'быстрые':
            return queryset.filter(
                cooking_time__range=(0, 10),
            )
        if self.value() == 'средние':
            return queryset.filter(
                cooking_time__range=(10, 30),
            )
        if self.value() == 'долгие':
            return queryset.all()

MAX_NUMBER_OF_TAGS_OR_INGREDIENTS_PER_PAGE = 15
NUMBER_OF_VISIBLE_CHATACTERS_IN_ADMIN_PANEL = 50

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'in_favorite_count',
        'cooking_time',
        'display_image',
        'display_tags',
        'display_ingredients'
    )
    list_filter = [CookingTimeListFilter]
    empty_value_display = '-empty-'
    readonly_fields = ['preview']

    def preview(self, recipe):
        return mark_safe(
            '<img style="max-width:200px; max-height:200px;"'
            f'src="{recipe.image.url}">'
        )

    @admin.display(description='Подписчики', empty_value=None)
    def in_favorite_count(self, recipe):
        return recipe.favorite.count()

    @admin.display(description='Фотография', empty_value=None)
    def display_image(self, recipe):
        return mark_safe(
            '<img style="max-width:200px; max-height:200px;"'
            f'src="{recipe.image.url}">'
        )

    @admin.display(description='Продукты', empty_value=None)
    def display_ingredients(self, recipe):
        return mark_safe(
            '<br>'.join(
                [
                    (ingredient.name)[
                        :NUMBER_OF_VISIBLE_CHATACTERS_IN_ADMIN_PANEL
                    ] + ', '
                    + ingredient.measurement_unit + ', '
                    + str(
                        get_object_or_404(
                            RecipeIngredient,
                            ingredient=ingredient,
                            recipe=recipe
                        ).amount
                    )
                    for ingredient in recipe.ingredients.all()[
                        :MAX_NUMBER_OF_TAGS_OR_INGREDIENTS_PER_PAGE
                    ]
                ]
            )
        )

    @admin.display(description='Теги', empty_value=None)
    def display_tags(self, recipe):
        return mark_safe(
            '<br>'.join(
                [
                    (tag.name)[:NUMBER_OF_VISIBLE_CHATACTERS_IN_ADMIN_PANEL]
                    for tag in recipe.tags.all()[
                        :MAX_NUMBER_OF_TAGS_OR_INGREDIENTS_PER_PAGE
                    ]
                ]
            )
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
