from django_filters.rest_framework import (
    FilterSet,
    filters
)

from recipes.models import (
    Ingredient,
    Recipe,
    User
)


# class MultiValueCharFilter(filters.BaseCSVFilter, filters.CharFilter):
#     def filter(self, qs, value):
#         values = value or []

#         for value in values:
#             qs = super(MultiValueCharFilter, self).filter(qs, value)

#         return qs


class AuthorAndTagFilter(FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')


class RecipeFilter(FilterSet):
    author = filters.CharFilter(field_name='author__id')
    # tags = MultiValueCharFilter(name='tags__name', lookup_expr='contains')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__name', lookup_expr='contains'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
