import os

import requests
from bs4 import BeautifulSoup as BSoup
from django.http import HttpResponse
from django.shortcuts import redirect, render

from newz.models import Headline, NewsSite

from .utils import *

import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO


@csrf_exempt
def plot(request):
    # Generate the data to plot
    x = [1, 2, 3, 4, 5]
    y = [1, 4, 9, 16, 25]

    # Create the Matplotlib figure
    fig, ax = plt.subplots()
    ax.plot(x, y)

    # Save the figure to a byte buffer
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)

    # Return the buffer as an HTTP response
    response = HttpResponse(buffer, content_type="image/png")
    return response


def resetHeadline(request):
    Headline.objects.all().delete()
    return redirect("../")


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

            main = article if newsSite.name == TPORTAL else article.find_all("a")[0]
            link = (
                (newsSite.hrefPrefix + main["href"])
                if not (
                    str(main["href"]).startswith("http")
                    or str(main["href"]).startswith("//www")
                )
                else str(main["href"])
            )
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
                if headlines.count() > 1:
                    print(f"More than one")
                else:
                    if len(str(link).split("/")) < 4:
                        print(f"Link to delte: {link}")
                        headlines.delete()
                    else:
                        categorise(headlines.all()[0], newsSite)
                continue

            print(f"New {newsSite.name} article {i}...")
            data_dir = f"testData/{newsSite.name.lower()}"
            if not os.path.exists(data_dir):
                os.mkdir(data_dir)
            with open(f"{data_dir}/article_{i}.html", "w") as file:
                file.write(str(article))

            new_headline = Headline()
            new_headline.title = title
            new_headline.url = link
            new_headline.image = image_src
            new_headline.news_site = newsSite
            if len(str(link).split("/")) < 4:
                print(f"Invalida link: {link}")
            else:
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

    try:
        url = str(str(headline.url).split("/")[3])
        category = url.replace("/", "")
    except Exception:
        print(f"Greška u {headline.url}")

    if (
        category == "sn"
        or category == "fightsite"
        or category == "sport"
        or category == "fit"
    ):
        headline.category = "sport"
    elif (
        category == "vijesti"
        or category == "zagreb"
        or category == "videovijesti"
        or category == "vijest"
        or category == "danas"
        or category == "hrvatska"
        or category == "regija"
        or category == "aktualno"
        or category == "eu"
        or category == "svijet"
        or category == "manjine"
        or category == "video"
    ):
        headline.category = "vijesti"
    elif category == "novac" or category == "gospodarstvo":
        headline.category = "financije"
    elif category == "vaumijau" or category == "native" or category == "webcafe":
        headline.category = "ostalo"
    elif (
        category == "showbiz"
        or category == "scena"
        or category == "show"
        or category == "showtime"
        or category == "magazi"
        or category == "magazin"
        or category == "hot"
        or category == "super1"
        or category == "zvijezde"
    ):
        headline.category = "showbusiness i scena"
    elif (
        category == "lifestyle"
        or category == "chill"
        or category == "shopping"
        or category == "zivot"
        or category == "pitanje-zdravlja"
        or category == "mame"
        or category == "food"
        or category == "bolja-ja"
    ):
        headline.category = "lifestyle"
    elif category == "moda" or category == "ljepota":
        headline.category = "moda"
    elif category == "kultura":
        headline.category = "kultura"
    elif category == "biznis":
        headline.category = "business"
    elif (
        category == "techsci"
        or category == "autoklub"
        or category == "autozona"
        or category == "techno"
        or category == "auto"
        or category == "tehno"
    ):
        headline.category = "tech i automobili"
    elif category == "crna-kronika" or category == "politika-kriminal":
        headline.category = "crna kronika"
    elif category == "horoskop" or category == "astro":
        headline.category = "horoskop"
    elif category == "promo":
        headline.category = "promo"
    elif category == "infokutak" or category == "znanost" or category == "edukacija":
        headline.category = "info i znanost"
    else:
        headline.category = "nekategorizirano"
        print(f"new category: {category} - link: {headline.url}")

    headline.save()
