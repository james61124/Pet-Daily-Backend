# Generated by Django 5.0 on 2024-01-01 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0003_pet_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproduct',
            name='height',
            field=models.DecimalField(decimal_places=0, default=100, max_digits=4),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='posX',
            field=models.DecimalField(decimal_places=0, default=50, max_digits=4),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='posY',
            field=models.DecimalField(decimal_places=0, default=50, max_digits=4),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='width',
            field=models.DecimalField(decimal_places=0, default=100, max_digits=4),
        ),
    ]
