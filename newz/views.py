import os

import requests
from bs4 import BeautifulSoup as BSoup
from django.http import HttpResponse
from django.shortcuts import redirect, render

from newz.models import Headline, NewsSite

from .utils import *


def scrape(request):
    session = requests.Session()
    session.headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}

    for newsSite in NewsSite.objects.all():
        print(f"Currently working on: {newsSite.name}")
        url = newsSite.url
        content = session.get(url, verify=False).content
        soup = BSoup(content, "html.parser")
        News = soup.find_all(newsSite.tag, {"class": newsSite.htmlClass})

        for i, article in enumerate(News):
            print(f"{newsSite.name} article {i}...")
            data_dir = f"testData/{newsSite.name.lower()}"
            if not os.path.exists(data_dir):
                os.mkdir(data_dir)
            with open(f"{data_dir}/article_{i}.html", "w") as file:
                file.write(str(article))

            main = article if newsSite.name == TPORTAL else article.find_all("a")[0]
            link = newsSite.hrefPrefix + main["href"]
            if main.find("img"):
                image_src = str(
                    main.find("img")["data-src" if newsSite.name == TPORTAL else "src"]
                )
                if not image_src.startswith("https"):
                    image_src = newsSite.hrefPrefix + image_src
            else:
                image_src = "https://picsum.photos/200"
            if "title" in main.attrs:
                title = main["title"]
            else:
                title = (
                    article.find_all(
                        "h2"
                        if newsSite.name == JUTARNJI
                        else ("h4" if newsSite.name == N1 else "h3")
                    )[0]
                    .contents[0]
                    .text
                )

            headlines = Headline.objects.filter(url=link, title=title)
            if headlines.count():
                continue

            new_headline = Headline()
            new_headline.title = title
            new_headline.url = link
            new_headline.image = image_src
            new_headline.news_site = newsSite
            categorise(new_headline, newsSite)
            new_headline.save()
    return redirect("../")


def news_list(request):
    allObject = [i for i in Headline.objects.all()]
    headlines = Headline.objects.all()[::-1]
    context = {
        "object_list": headlines,
    }
    vecernji = [
        headline
        for headline in Headline.objects.filter(
            news_site__url="https://www.vecernji.hr/najnovije-vijesti"
        ).all()
    ]
    jutarnji = [
        headline
        for headline in Headline.objects.filter(
            news_site__url="https://www.jutarnji.hr/vijesti/najnovije"
        ).all()
    ]
    index = [
        headline
        for headline in Headline.objects.filter(
            news_site__url="https://www.index.hr/najnovije"
        ).all()
    ]
    net = [
        headline
        for headline in Headline.objects.filter(
            news_site__url="https://net.hr/najnovije/stranica-1"
        ).all()
    ]
    hrt = [
        headline
        for headline in Headline.objects.filter(
            news_site__url="https://vijesti.hrt.hr/"
        ).all()
    ]
    return render(request, "home.html", context)


def categorise(headline: Headline, newsSite: NewsSite):
    print("inside categorise")


#     url = headline.url.replace(newsSite.hrefPrefix + "/", "")
#     index = url.find("/", 0)
#     category = url[0:index]
#     if category == "sn" or category == "fightsite" or category == "sport":
#         headline.category = "sport"
#     elif category == "vijesti" or category == "zagreb":
#         headline.category = "vijesti"
#     elif category == "novac":
#         headline.category = "financije"
#     elif category == "vaumijau":
#         headline.category = "ostalo"
#     elif category == "showbiz" or category == "scena":
#         headline.category = "showbusiness i scena"
#     elif category == "lifestyle":
#         headline.category = "lifestyle"
#     elif category == "kultura":
#         headline.category = "kultura"
#     elif category == "biznis":
#         headline.category = "business"
#     elif category == "techsci" or category == "autoklub":
#         headline.category = "tech i automobili"
