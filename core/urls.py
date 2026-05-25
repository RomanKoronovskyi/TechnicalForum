from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('', include('forum.urls', namespace='forum')),
]