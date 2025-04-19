from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from reviews.views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reviews.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)