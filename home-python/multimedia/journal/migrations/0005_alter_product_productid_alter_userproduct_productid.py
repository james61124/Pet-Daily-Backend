# Generated by Django 5.0 on 2024-01-01 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0004_alter_userproduct_height_alter_userproduct_posx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='productid',
            field=models.CharField(max_length=400),
        ),
        migrations.AlterField(
            model_name='userproduct',
            name='productid',
            field=models.CharField(max_length=400),
        ),
    ]