from rest_framework.serializers import ValidationError

from recipes.models import Ingredient


def validate_ingredient(ingredients):
    if not ingredients:
        raise ValidationError('Это поле обязательно')
    unique_ingridients_list = []
    for ingredient in ingredients:
        if ingredient.get('amount') is None:
            raise ValidationError('Укажите колличество')
        if int(ingredient.get('amount')) < 1:
            raise ValidationError('Колличество не может быть меньше 1')
        ingredient_id = ingredient.get('id')
        if ingredient_id in unique_ingridients_list:
            raise ValidationError('Ингредиенты должны быть разными')
        unique_ingridients_list.append(ingredient_id)
        if not Ingredient.objects.filter(id=ingredient_id).exists():
            raise ValidationError('Такого ингредиента нет в базе')
