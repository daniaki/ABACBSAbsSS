# Generated by Django 2.0 on 2018-07-07 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abstract', '0011_auto_20180707_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(default=None, verbose_name='Comments'),
        ),
    ]
