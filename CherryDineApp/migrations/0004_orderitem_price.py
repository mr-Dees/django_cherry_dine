# Generated by Django 5.1.3 on 2024-12-02 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("CherryDineApp", "0003_alter_order_options_order_total_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="price",
            field=models.DecimalField(decimal_places=2, default=50, max_digits=10),
            preserve_default=False,
        ),
    ]