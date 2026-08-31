from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Redirect root to Swagger UI documentation
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('docs/', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('swagger/', RedirectView.as_view(url='/api/docs/', permanent=False)),

    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # Swagger / OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
