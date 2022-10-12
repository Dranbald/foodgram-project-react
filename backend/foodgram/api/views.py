from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import(Favorite, Ingredient, Recipe, RecipeIngredient,
                           ShoppingCart, Tag)
from .filters import RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthenticatedAuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    pass


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipeFilter
    permission_classes = [IsAuthenticatedAuthorOrReadOnly]

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(request.method)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        carts = request.user.cart.all()
        amount_dict = {}
        unit_dict = {}
        for cart in carts:
            recipe = cart.recipe
            for ingredient in recipe.ingredients.all():
                unit_dict[ingredient.name] = ingredient.measurement_unit
                amount_storage = get_object_or_404(
                    RecipeIngredient,
                    recipe=recipe,
                    ingredient=ingredient
                )
                amount = amount_storage.amount
                existing = amount_dict.get(ingredient.name)
                if existing:
                    amount_dict[ingredient.name] = (
                        int(amount) + int(existing)
                    )
                else:
                    amount_dict[ingredient.name] = int(amount)
            empty_str = ''
            for i in range(0, len(amount_dict)):
                new_str = (
                    str(list(amount_dict.keys())[i]) + ' (' +
                    str(unit_dict[list(amount_dict.keys())[i]]) +
                    ') - ' + str(list(amount_dict.values())[i])
                )
                empty_str = empty_str + new_str + '\n'
            response = HttpResponse(
                empty_str,
                content_typte='text/plain;charset=UTF-8'
            )
            response['Content-Disposition'] = (
                'attachment;'
                'filename="shopping_cart.txt"'
            )
            return response


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
