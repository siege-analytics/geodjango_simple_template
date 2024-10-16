# Generated by Django 5.1.2 on 2024-10-13 23:24

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0007_alter_united_states_address_latitude_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="admin_level_1",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=5070),
        ),
        migrations.AlterField(
            model_name="admin_level_2",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=5070),
        ),
        migrations.AlterField(
            model_name="admin_level_3",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=5070),
        ),
        migrations.AlterField(
            model_name="admin_level_4",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=5070),
        ),
        migrations.AlterField(
            model_name="admin_level_5",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=5070),
        ),
        migrations.AlterField(
            model_name="country",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(
                blank=True, default=None, null=True, srid=5070
            ),
        ),
        migrations.AlterField(
            model_name="locality",
            name="geom",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=5070),
        ),
        migrations.AlterField(
            model_name="place",
            name="geom",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, default=None, null=True, srid=5070
            ),
        ),
        migrations.AlterField(
            model_name="united_states_address",
            name="geom",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, default=None, null=True, srid=5070
            ),
        ),
    ]
