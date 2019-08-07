from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('login/', include('config.urls')),
    path('admin/', admin.site.urls),
]
