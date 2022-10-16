from recipes.models import Recipe
from rest_framework import serializers

from .models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AuthorSerializer(UserSerializer):
    """Сериализатор для автора рецепта"""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta(UserSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if (
            self.context.get('request') is not None
            and self.context.get('request').user.is_authenticated
        ):
            return Follow.objects.filter(
                user=self.context.get('request').user,
                following=obj
            ).exists()
        return False


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки на автора"""
    email = serializers.ReadOnlyField(source='following.id')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user,
            following=obj.following
        ).exists()

    def get_recipes(self, obj):
        from api.serializers import CartSerializer
        if self.context:
            recipes_limit = self.context['request'].GET.get('recipes_limit')
            if recipes_limit:
                queryset = Recipe.objects.filter(
                    author=obj.following
                )[:int(recipes_limit)]
        else:
            queryset = Recipe.objects.filter(
                author=obj.following
            )
        return CartSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following).count()

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]


class PasswordSerializer(serializers.ModelSerializer):
    """Сериализатор смены пароля от учетной записи"""
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
    """Сериализатор для Токена"""
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
