from django.contrib import admin
from django.urls import include, path
from newz.views import scrape, scrapeAll, news_list

urlpatterns = [
    path('scrape/', scrape, name="scrape"),
    path('scrape-all/', scrapeAll, name="scrapeAll"),
    path('', news_list, name="home"),
    path('admin/', admin.site.urls),
]
