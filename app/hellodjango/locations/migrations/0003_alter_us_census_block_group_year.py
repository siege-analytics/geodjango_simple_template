# Generated by Django 5.1.3 on 2024-11-15 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_us_census_block_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="us_census_block_group",
            name="year",
            field=models.IntegerField(),
        ),
    ]