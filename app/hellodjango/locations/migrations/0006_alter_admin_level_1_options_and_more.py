# Generated by Django 5.0.7 on 2024-07-12 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "locations",
            "0005_alter_admin_level_1_cc_1_alter_admin_level_1_country_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="admin_level_1",
            options={"ordering": ["gid_1"]},
        ),
        migrations.AlterModelOptions(
            name="admin_level_2",
            options={"ordering": ["gid_2"]},
        ),
        migrations.AlterModelOptions(
            name="admin_level_3",
            options={"ordering": ["gid_3"]},
        ),
        migrations.AlterModelOptions(
            name="admin_level_4",
            options={"ordering": ["gid_4"]},
        ),
        migrations.AlterModelOptions(
            name="admin_level_5",
            options={"ordering": ["gid_5"]},
        ),
        migrations.AlterModelOptions(
            name="country",
            options={"ordering": ["country"]},
        ),
    ]
