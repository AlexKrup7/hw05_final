from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from .views import GroupViewSet, PostViewSet, FollowViewSet, CommentViewSet

router_ver1 = routers.DefaultRouter()
router_ver1.register(r'groups', GroupViewSet, basename='groups')
router_ver1.register(r'posts', PostViewSet, basename='posts')
router_ver1.register(r'follow', FollowViewSet, basename='follow')
router_ver1.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet,
                     basename='comments')

urlpatterns = [
    path('v1/jwt/create/', TokenObtainPairView.as_view()),
    path('v1/jwt/refresh/', TokenRefreshView.as_view()),
    path('v1/jwt/verify/', TokenVerifyView.as_view()),
    path('v1/', include(router_ver1.urls)),
]
