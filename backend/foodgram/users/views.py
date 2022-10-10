from django.shortcuts import get_object_or_404

from djoser import utils, views
from djoser.conf import settings
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import PageLimitPagination
from .models import Follow, User
from .serializers import FollowSerializer, PasswordSerializer, TokenSerializer, UserSerializer



class CreateViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class UserViewSet(CreateViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class =PageLimitPagination
    permission_classes = (AllowAny,)
    
    @action(
        detail=False,
        methods=['GET',],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=False,
        methods=['POST',],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = PasswordSerializer
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        if user.password != password:
            raise exceptions.ValidationError('Неверный пароль')
        user.password = new_password
        user.save(update_fields=['password'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET',],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        follows = request.user.follower.all()
        page = self.paginate_queryset(follows)
        if page is not None:
            serializer = FollowSerializer(
                page,
                many=True,
                context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            follows,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)


class FollowView(APIView):
    def get_serializer_context(self):
        return {
            'format': self.format_kwarg,
            'request': self.request,
            'view': self            
        }

    def post(self, request, *args, **kwargs):
        following_id = self.kwargs.get('pk')
        following = get_object_or_404(User, id=following_id)
        user = request.user
        try:
            follow = Follow.objects.create(
                user=user,
                following=following
            )
        except Exception:
            response = {'errors': 'Подписаться невозможно!'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        serializer = FollowSerializer(
            follow,
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        objects = request.user.follower.all()
        following_id = self.kwargs.get('pk')
        following = get_object_or_404(User, id=following_id)
        objects.filter(following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenCreateView(views.TokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


def get_token_for_user(user):
    token = Token.objects.create(user=user)
    return {
        'auth_token': str(token.key),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        email=request.data.get('email')
    )
    if user.password == request.data.get('password'):
        return Response(
            get_token_for_user(user),
            status=status.HTTP_201_CREATED
        )
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_token(request):
    user = request.user
    user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
