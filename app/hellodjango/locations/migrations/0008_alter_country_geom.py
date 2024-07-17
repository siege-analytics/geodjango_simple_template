# Generated by Django 5.0.7 on 2024-07-12 20:50

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0007_alter_timezone_geom"),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(
                blank=True, default=None, null=True, srid=4326
            ),
        ),
    ]