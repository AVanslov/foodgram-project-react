from django.contrib import admin
from django.urls import path, include

from foodgram_api.views import (
    user_list,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('api/users/', user_list),
]
