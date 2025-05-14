# teams/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from projects.views import ProjectViewSet
from .views import TeamViewSet, PlayerViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'players', PlayerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
