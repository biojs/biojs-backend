from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    url(r'^(?i)admin/', admin.site.urls),
    url(r'^',include("main.urls")),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, serve, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, serve, document_root=settings.MEDIA_ROOT)
