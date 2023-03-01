from django import forms
from newz import models

CATEGORIES = (
    (None, '-------'),
    ('sport', 'Sport'),
    ('vijesti', 'Vijesti'),
    ('financije', 'Financije'),
    ('ostalo', 'Ostalo'),
    ('showbusiness i scena', 'Showbiz'),
    ('lifestyle', 'Lifestyle'),
    ('moda', 'Moda'),
    ('kultura', 'Kultura'),
    ('business', 'Business'),
    ('tech i automobili', 'Tech i automobili'),
    ('crna kronika', 'Crna kronika'),
    ('horoskop', 'Horoskop'),
    ('promo', 'Promo'),
    ('info i znanost', 'Info i znanost'),
    ('nekategorizirano', 'Nekategorizirano',),
)


class FilterForm(forms.Form):
    news_site = forms.ModelChoiceField(queryset=models.NewsSite.objects.all(), label='Portal', required=False)
    category = forms.ChoiceField(choices=CATEGORIES, required=False)
