from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import(Favorite, Ingredient, Recipe, RecipeIngredient,
                           ShoppingCart, Tag)
from .filters import IngredientFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthenticatedAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer, 
                          TagSerializer, CartSerializer)


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    pass


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


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

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return create_recipes_list(request, pk, ShoppingCart)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return create_recipes_list(request, pk, Favorite)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_dict = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=request.user.shopping_cart.values('recipe')
        ).select_related('ingredient')
        for obj in ingredients:
            ingredient = obj.ingredient.name
            if ingredient not in shopping_dict:
                shopping_dict[ingredient] = {
                    'measurement_unit': obj.ingredient.measurement_unit,
                    'amount': obj.amount
                }
            else:
                shopping_dict[ingredient]['amount'] += obj.amount
        shopping_cart = '{username} вот твой список покупок \n'
        download_cart = shopping_cart.format(username=request.user.username)
        for ingredient in shopping_dict:
            download_cart += (
                f'{ingredient} '
                f'({shopping_dict[ingredient]["measurement_unit"]}) '
                f'- {shopping_dict[ingredient]["amount"]}\n'
            )
        download_cart += 'foodgram'
        response = HttpResponse(
            download_cart,
            content_type='text/plain;charset=UTF-8',
        )
        response['Content-Disposition'] = (
            'attachment;'
            'filename="shopping_cart.txt"'
        )
        return response


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


def create_recipes_list(request, pk, model):
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        obj, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if created:
            serializer = CartSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': 'Рецепт уже в списке'},
            status=status.HTTP_400_BAD_REQUEST
        )
    obj = model.objects.filter(
        user=request.user,
        recipe=recipe
    )
    if obj:
        obj.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    return Response(
        {'errors': 'Нет рецепта'}, status=status.HTTP_400_BAD_REQUEST
    )
