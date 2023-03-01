from django.db import models


class NewsSite(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = models.CharField(max_length=200)
    hrefPrefix = models.CharField(max_length=200, blank=True)
    tag = models.CharField(max_length=100, blank=True)
    htmlClass = models.CharField(max_length=100, blank=True)
    locale = models.CharField(max_length=2, default='hr')

    def __str__(self):
        return self.name


class Headline(models.Model):
    title = models.CharField(max_length=200)
    image = models.URLField(null=True, blank=True)
    url = models.TextField()
    news_site = models.ForeignKey(NewsSite, on_delete=models.CASCADE, blank=False)
    category = models.CharField(max_length=50, blank=True)

    # toString function
    def __str__(self):
        return self.title
