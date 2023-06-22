# Generated by Django 4.1.7 on 2023-06-11 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_order_prodigi_order_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('author', models.CharField(max_length=100)),
                ('date', models.DateField(auto_now_add=True)),
                ('category', models.CharField(max_length=100)),
                ('main_image', models.ImageField(blank=True, null=True, upload_to='articles/')),
            ],
        ),
    ]