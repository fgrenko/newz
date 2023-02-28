from django.contrib import admin
from django.urls import include, path

from newz.views import news_list, resetHeadline, scrape

urlpatterns = [
    path("scrape/", scrape, name="scrape"),
    path("resetHeadline/", resetHeadline, name="resetHeadline"),
    path("", news_list, name="home"),
    path("admin/", admin.site.urls),
]
