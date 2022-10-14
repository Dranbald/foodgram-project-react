from django.shortcuts import get_object_or_404

from djoser import utils, views
from djoser.conf import settings
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import PageLimitPagination
from .models import Follow, User
from .serializers import (AuthorSerializer, FollowSerializer, 
                          PasswordSerializer, UserSerializer)



class CreateViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class UserViewSet(CreateViewSet):
    queryset = User.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = (AllowAny,)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AuthorSerializer
        return UserSerializer

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = AuthorSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.check_password(request.data.get('current_password')):
            request.user.set_password(request.data.get('new_password'))
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(
        detail=False,
        methods=['GET',],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(
            user=request.user
        ).select_related('following')
        serializer = FollowSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Подписаться на себя невозможно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = Follow.objects.get_or_create(
                user=request.user, following=author
            )
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FollowSerializer(subscription)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        subscription = Follow.objects.filter(
            user=request.user, following=author
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'На этого полльзователя вы не подписаны'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TokenCreateView(views.TokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )
