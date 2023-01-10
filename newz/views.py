from django.http import HttpResponse
import requests
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup as BSoup
from newz.models import Headline
from newz.models import NewsSite

JUTARNJI = "Jutarnji List"
VECERNJI = "Večernji List"
INDEX = "Index"


def scrape(request):
    session = requests.Session()
    session.headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
    newsSite = NewsSite.objects.filter(name=INDEX)
    newsSite = newsSite.first()
    url = newsSite.url
    content = session.get(url, verify=False).content
    soup = BSoup(content, "html.parser")
    News = soup.find_all(newsSite.tag, {"class": newsSite.htmlClass})
    for article in News:
        main = article.find_all('a')[0]
        link = main['href']
        # image_src = str(main.find('img')['src']).split(" ")[-4]
        image_src = str(main.find('img')['src'])
        if 'title' in main:
            title = main['title']
        else:
            title = article.find_all('h2')[0].contents[0]
        headlines = Headline.objects.filter(url=link, title=title)
        if headlines.count():
            continue

        new_headline = Headline()
        new_headline.title = title
        new_headline.news_site = newsSite
        new_headline.url = link
        new_headline.image = image_src

        new_headline.save()
    return redirect("../")


def scrapeAll(request):
    session = requests.Session()
    session.headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
    for newsSite in NewsSite.objects.all():
        url = newsSite.url
        content = session.get(url, verify=False).content
        soup = BSoup(content, "html.parser")
        News = soup.find_all(newsSite.tag, {"class": newsSite.htmlClass})
        for article in News:
            main = article.find_all('a')[0]
            link = newsSite.hrefPrefix + main['href']
            # image_src = str(main.find('img')['src']).split(" ")[-4]
            image_src = str(main.find('img')['src'])
            if not image_src.startswith('https'):
                image_src = newsSite.hrefPrefix + image_src
            if 'title' in main.attrs:
                title = main['title']
            else:
                title = article.find_all('h2')[0].contents[0]
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
    headlines = Headline.objects.all()[::-1]
    context = {
        'object_list': headlines,
    }
    return render(request, "home.html", context)


def categorise(headline: Headline, newsSite: NewsSite):
    url = headline.url.replace(newsSite.hrefPrefix + '/', '')
    index = url.find('/', 0)
    category = url[0:index]
    if category == 'sn' or category == 'fightsite' or category == 'sport':
        headline.category = 'sport'
    elif category == 'vijesti' or category == 'zagreb':
        headline.category = 'vijesti'
    elif category == 'novac':
        headline.category = 'financije'
    elif category == 'vaumijau':
        headline.category = 'ostalo'
    elif category == 'showbiz' or category == 'scena':
        headline.category = 'showbusiness i scena'
    elif category == 'lifestyle':
        headline.category = 'lifestyle'
    elif category == 'kultura':
        headline.category = 'kultura'
    elif category == 'biznis':
        headline.category = 'business'
    elif category == 'techsci' or category == 'autoklub':
        headline.category = 'tech i automobili'
