from django.urls import include, path

from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import TokenCreateView, UserViewSet

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')

auth = [
    path('login/', TokenCreateView.as_view(), name='login'),
    path('logout/', TokenDestroyView.as_view(), name='logout'),
]


urlpatterns = [
    path('', include(router_v1.urls)),
    path('token/', include(auth)),
]
