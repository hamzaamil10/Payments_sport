from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import MatchViewSet

router = DefaultRouter()
router.register("matches", MatchViewSet, basename="match")

urlpatterns = [
    path("", include(router.urls)),
]
