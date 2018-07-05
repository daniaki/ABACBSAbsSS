# Generated by Django 2.0 on 2018-07-05 01:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('abstract', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstract',
            name='submitter',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='abstracts', related_query_name='abstract', to=settings.AUTH_USER_MODEL, verbose_name='Submitter'),
        ),
    ]
