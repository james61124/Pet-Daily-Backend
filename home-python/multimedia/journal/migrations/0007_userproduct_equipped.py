# Generated by Django 5.0 on 2023-12-31 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0006_userproduct_height_userproduct_width_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproduct',
            name='equipped',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=4),
        ),
    ]