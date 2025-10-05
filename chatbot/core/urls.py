from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path('', lambda r: redirect('chat')),
    path('admin/', admin.site.urls),
    path('contas/', include('contas.urls')),
    path('ia/', include('ia.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
