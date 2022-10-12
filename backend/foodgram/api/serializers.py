import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import(Favorite, Ingredient,Recipe, RecipeIngredient,
                           ShoppingCart, Tag)
from users.serializers import AuthorSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        validators = serializers.UniqueTogetherValidator(
            queryset=RecipeIngredient.objects.all(),
            fields=('recipe', 'ingredient')
        )


class TagSerializer(serializers.ModelSerializer):

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


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredients_amounts',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
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

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(
            ingredients,
            many=True).data

    def get_is_favorited(self, instance):
        user_id = self.context['request'].user.id
        recipe_id = instance.id
        try:
            return Favorite.objects.filter(
                user=user_id,
                recipe=recipe_id
            ).exists()
        except Exception:
            return False

    def get_is_shopping_cart(self, instance):
        user_id = self.context['request'].user.id
        recipe_id = instance.id
        try:
            return ShoppingCart.objects.filter(
                user=user_id,
                recipe=recipe_id
            ).exists()
        except Exception:
            return False

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиент уже в списке'
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) <= 0:
                raise serializers.ValidationError(
                    'Ингредиентов должно быть 1 или более'
                )
        data['ingredients'] = ingredients
        return data


    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, 
            **validated_data
        )
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
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.image = validated_data.get('image')
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


class CartSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
