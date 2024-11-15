# Generated by Django 5.1.3 on 2024-11-15 19:47

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0006_united_states_state_legislative_district_upper"),
    ]

    operations = [
        migrations.CreateModel(
            name="United_States_Census_Tabulation_Block",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("statefp20", models.CharField(max_length=2)),
                ("countyfp20", models.CharField(max_length=3)),
                ("tractce20", models.CharField(max_length=6)),
                ("blockce20", models.CharField(max_length=4)),
                ("geoid20", models.CharField(max_length=15)),
                ("geoidfq20", models.CharField(max_length=24)),
                ("name20", models.CharField(max_length=10)),
                ("mtfcc20", models.CharField(max_length=5)),
                ("ur20", models.CharField(max_length=1)),
                ("uace20", models.CharField(max_length=5)),
                ("funcstat20", models.CharField(max_length=1)),
                ("aland20", models.BigIntegerField()),
                ("awater20", models.BigIntegerField()),
                ("intptlat20", models.CharField(max_length=11)),
                ("intptlon20", models.CharField(max_length=12)),
                ("housing20", models.BigIntegerField()),
                ("pop20", models.BigIntegerField()),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.MultiPolygonField(srid=4269),
                ),
                ("year", models.IntegerField()),
            ],
        ),
    ]