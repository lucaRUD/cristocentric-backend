# Generated by Django 4.1.7 on 2023-05-26 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_product_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='colors',
            field=models.JSONField(default='NO COLOR'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.JSONField(default='NO SIZE'),
            preserve_default=False,
        ),
    ]
