# Generated by Django 2.0 on 2018-07-05 02:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('abstract', '0003_auto_20180705_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstract',
            name='submitter',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='abstracts', to=settings.AUTH_USER_MODEL, verbose_name='Submitter'),
        ),
    ]
