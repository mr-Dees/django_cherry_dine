# Generated by Django 5.1.3 on 2024-12-02 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("CherryDineApp", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-created_at"]},
        ),
    ]
