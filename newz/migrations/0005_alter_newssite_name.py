# Generated by Django 4.1.4 on 2023-01-10 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newz", "0004_newssite_hrefprefix"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newssite",
            name="name",
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
