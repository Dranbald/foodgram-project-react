from django_filters import (FilterSet, NumberFilter,
                            ModelMultipleChoiceFilter)
from recipes.models import Recipe, Tag

class RecipeFilter(FilterSet):
    is_favorited = NumberFilter(
        method='filter_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        method='filter_is_shopping_cart'
    )
    author = NumberFilter(
        field_name='filter_author'
    )
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            return queryset.filter(favorited=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            return queryset.filter(in_shopping_cart=self.request.user)

    def filter_author(self, queryset, name, value):
        if value == 'me':
            return queryset.filter(author=self.request.user)
        return queryset.filter(author=value)

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )
