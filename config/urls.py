from django.contrib import admin
from django.urls import path
from shop import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<int:pk>/", views.product, name="product"),
    path("stores/", views.stores, name="stores"),
    path("api/catalog/", views.api_catalog, name="api_catalog"),
    path("api/stores/", views.api_stores, name="api_stores"),
]
