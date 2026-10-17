from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "EcoIndustrial – Administration"
admin.site.site_title = "EcoIndustrial"
admin.site.index_title = "Tableau de bord"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
