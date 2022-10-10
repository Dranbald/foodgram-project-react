from rest_framework import serializers

from recipes.models import Recipe
from .models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField(
        method_name='subscription'
    )
    
    def subscription(self, instance):
        try:
            user = self.context['request'].user
        except Exception:
            user = instance
        author = instance
        try:
            return Follow.objects.filter(
                user=user, following=author).exists()
        except Exception:
            return False

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )

    def create_user(self, validated_data):
        password = validated_data.pop('password')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='following.id')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    
    def subscription(self, instance):
        user = self.context['request'].user
        author = instance.following
        try:
            return Follow.objects.filter(
                user=user, following=author).exists()
        except Exception:
            return False

    def get_recipe(self, instance):
        author = instance.following
        recipes = author.recipes.all()
        recipes_limit = self.context['request'].query_params.get('recipes_limit')
        if recipes_limit:
            recipes = author.recipes.all()[:int(recipes_limit)]
        return CartSerializer(recipes, many=True).data
    #
    def recipe_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
#
    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]


class PasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        required=True,
        max_length=150
    )
    current_password = serializers.CharField(
        required=True,
        max_length=150
    )
    
    class Meta:
        model = User
        fields = (
            'new_password',
            'current_password'
        )


class TokenSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        required=True,
        max_length=150
    )
    password = serializers.CharField(
        required=True,
        max_length=150
    )

    class Meta:
        model = User
        fields = ['email', 'password']
