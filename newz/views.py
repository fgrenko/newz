import base64
import math
import os
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup as BSoup
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from newz.models import Headline, NewsSite
from .forms import FilterForm

from .utils import *
from django.db.models import Q


def getCategoryCoverage():
    data = (
        Headline.objects.all()
        .values("news_site__name", "category")
        .annotate(count=models.Count("id"))
    )

    for headline in data:
        print(headline)

    df = pd.DataFrame(data)

    pivot_table = df.pivot(
        index="category", columns="news_site__name", values="count"
    ).fillna(0)

    print(pivot_table)

    # Create a subplots grid with a plot for each category
    fig, axs = plt.subplots(nrows=len(categories), figsize=(10, 20))

    # Loop over the categories and plot a bar chart for each category
    for i, category in enumerate(categories):
        # if category in pivot_table.columns:
        plot = pivot_table.loc[category].plot(kind="bar", legend=False, ax=axs[i])
        if i < len(categories) - 1:
            plot.set_xticklabels([])
        plot.set_title(category, pad=10)
        plot.set_xlabel("")
        plot.set_ylabel("Broj")

    # Adjust the layout of the subplots
    plt.subplots_adjust(
        left=0.125,
        right=0.9,
        bottom=0.1,
        top=0.9,
        wspace=0.5,
        hspace=0.5,
    )
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    data_dir = f"testData/images"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    plt.savefig(f"{data_dir}/categoryCoverage.png", bbox_inches="tight")

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode("utf-8")

    plt.clf()

    return graphic


def getCategorySharePlot():
    data = (
        Headline.objects.all()
        .values("news_site__name", "category")
        .annotate(count=models.Count("id"))
    )
    df = pd.DataFrame(data)

    print(len(NewsSite.objects.all()))

    pivot_table = df.pivot(
        index="category", columns="news_site__name", values="count"
    ).fillna(0)

    normalized_table = pivot_table.div(pivot_table.sum(axis=1), axis=0)

    num_cols = 2
    num_rows = math.ceil(len(NewsSite.objects.all()) / num_cols)
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(16, 16))

    for i, (colname, coldata) in enumerate(normalized_table.iteritems()):
        ax = axes[i // num_cols, i % num_cols]
        coldata.plot(
            kind="barh", stacked=True, ax=ax, color=plt.cm.get_cmap("tab20").colors
        )
        ax.set_title(colname)
        ax.set_xlabel("Udio")

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    data_dir = f"testData/images"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    plt.savefig(f"{data_dir}/categoryShare.png", bbox_inches="tight")

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode("utf-8")

    plt.clf()

    return graphic


def getCategoryCount():
    data = Headline.objects.all()

    categoryCounts = {}

    for category in categories:
        categoryCounts[category] = len(
            [obj for obj in data if obj.category == category]
        )

    print(categoryCounts)

    plt.figure(figsize=(10, 6))
    plt.bar(categoryCounts.keys(), categoryCounts.values())
    plt.title("Broj po kategoriji")
    plt.xlabel("Kategorije")
    plt.ylabel("Broj")
    plt.xticks(rotation="vertical")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    data_dir = f"testData/images"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    plt.savefig(f"{data_dir}/categoryCounts.png", bbox_inches="tight")

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode("utf-8")

    plt.clf()

    return graphic


def plot(request):
    context = {
        "categoryCounts": "data:image/png;base64," + getCategoryCount(),
        "categoryShare": "data:image/png;base64," + getCategorySharePlot(),
        "categorycoverage": "data:image/png;base64," + getCategoryCoverage(),
    }
    return render(request, "plots.html", context)


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

            main = (
                article
                if newsSite.name == TPORTAL
                else article.find_all("a")[1 if newsSite.name == INDEX else 0]
            )
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

                if newsSite.name == N1:
                    title = article.find_all("h4")[0].find_all("a")[0].contents[0].text
                else:
                    title = (
                        article.find_all("h2" if newsSite.name == JUTARNJI else "h3")[0]
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
            try:
                data_dir = f"testData/{newsSite.name.lower()}"
                if not os.path.exists(data_dir):
                    os.mkdir(data_dir)
                with open(f"{data_dir}/article_{i}.html", "w") as file:
                    file.write(str(article))
            except (Exception):
                print(Exception)

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

    print(request)

    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = FilterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            filters = Q()
            news_site = form.data.get("news_site")
            cancel = form.data.get("cancel")
            category = form.data.get("category")

            if cancel:
                return HttpResponseRedirect("/")
            if news_site:
                filters &= Q(news_site=news_site)
            if category:
                filters &= Q(category=category)

            headlines = Headline.objects.filter(filters)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = FilterForm()

    if "headlines" not in locals():
        headlines = Headline.objects.all()[::-1]

    paginator = Paginator(headlines, 21)
    page = request.GET.get("page", 1)
    object_list = paginator.page(page)
    page_range = paginator.get_elided_page_range(number=page)

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

    context = {
        "object_list": object_list,
        "page_range": page_range,
        "form": form,
    }

    data_dir = "testData"
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

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
        or category == "rijeka"
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
        or category == "ljubimci"
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
        or category == "zdravlje"
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
