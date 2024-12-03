# Generated by Django 5.1.3 on 2024-12-02 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("CherryDineApp", "0002_alter_order_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={},
        ),
        migrations.AddField(
            model_name="order",
            name="total_price",
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]