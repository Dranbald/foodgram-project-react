from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import TokenCreateView, UserViewSet

router = DefaultRouter()

router.register('', UserViewSet, basename='users')

auth = [
    path('login/', TokenCreateView.as_view(), name='login'),
    path('logout/', TokenDestroyView.as_view(), name='logout'),
]


urlpatterns = [
    path('', include(router.urls)),
    path('token/', include(auth)),
]
