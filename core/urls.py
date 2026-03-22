from django.contrib import admin
from django.urls import path, include
from core.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('products/', include('apps.products.urls')),
    path('purchases/', include('apps.purchases.urls')),
    path('sales/', include('apps.sales.urls')),
]
