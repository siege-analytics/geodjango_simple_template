# Generated by Django 5.0.7 on 2024-07-24 19:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_locality_place"),
    ]

    operations = [
        migrations.AddField(
            model_name="locality",
            name="address",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                to="locations.united_states_address",
            ),
        ),
        migrations.AddField(
            model_name="place",
            name="address",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                to="locations.united_states_address",
            ),
        ),
    ]
