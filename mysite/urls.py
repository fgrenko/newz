from django.contrib import admin
from django.urls import include, path

from newz.views import news_list, scrape

urlpatterns = [
    path("scrape/", scrape, name="scrape"),
    path("", news_list, name="home"),
    path("admin/", admin.site.urls),
]
