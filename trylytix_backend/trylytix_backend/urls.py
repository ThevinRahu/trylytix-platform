from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http import JsonResponse

urlpatterns = [
    path('', lambda request: HttpResponse("OK")),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('projects.urls')),
    path('api/', include('teams.urls')),
    path('api/', include('matches.urls')),
    path('api/', include('events.urls')),
]
