# Generated by Django 5.1.2 on 2024-10-11 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0004_remove_locality_address_alter_place_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="united_states_address",
            name="latitude",
            field=models.FloatField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="united_states_address",
            name="longitude",
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
