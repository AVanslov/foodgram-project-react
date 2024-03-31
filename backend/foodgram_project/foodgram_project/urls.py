from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from foodgram_api.views import (
    user_list,
    recipe_list,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('api/users/', user_list),
    path('api/recipes/', recipe_list),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
