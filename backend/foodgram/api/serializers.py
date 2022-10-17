import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import AuthorSerializer, UserSerializer

from .validatiors import validate_ingredient


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов"""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в составе рецепта"""
    id = serializers.CharField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        validators = serializers.UniqueTogetherValidator(
            queryset=RecipeIngredient.objects.all(),
            fields=('recipe', 'ingredient')
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class TagsField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        return TagSerializer(value).data


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецептов"""
    author = AuthorSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
        read_only=True
    )
    image = Base64ImageField(
        max_length=None
    )
    tags = TagsField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = [
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(
            recipe=obj
        )
        return RecipeIngredientSerializer(
            ingredients,
            many=True).data

    def get_is_favorited(self, obj):
        return favorite_or_shop_cart(self, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return favorite_or_shop_cart(self, obj, ShoppingCart)

    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        validate_ingredient(ingredients)
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_data.get('id')
            )
            amount = int(ingredient_data.get('amount'))
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.initial_data.get('ingredients')
        validate_ingredient(ingredients)
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        for ingredient_data in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_data.get('id')
            )
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data.get('amount')
            )
        for tag in tags:
            instance.tags.add(tag)
        instance.save()
        return instance


class ReadRecipeSerializer(WriteRecipeSerializer):
    """Сериализатор для просмотра рецептов"""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


def favorite_or_shop_cart(self, obj, model):
    user = self.context.get('request').user
    if user.is_anonymous:
        return False
    return model.objects.filter(
        user=user,
        recipe=obj.id
    ).exists()
