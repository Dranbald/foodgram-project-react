from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import (Filter, FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        method='filter_is_shopping_cart'
    )
    author = Filter(
        method='filter_author'
    )
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            return queryset.filter(is_favorited=self.request.user)
        return queryset

    def filter_is_shopping_cart(self, queryset, name, value):
        if value == 1:
            return queryset.filter(is_in_shopping_cart=self.request.user)
        return queryset

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


class IngredientFilter(FilterSet):
    name = Filter(
        method='filter_name'
    )

    def filter_name(self, queryset, name, value):
        data = queryset.filter(name__contains=value)
        startswith = ExpressionWrapper(
            Q(name__startswith=value),
            output_field=BooleanField()
        )
        return data.annotate(startswith=startswith).order_by('-startswith')
