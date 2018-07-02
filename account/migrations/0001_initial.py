# Generated by Django 2.0.6 on 2018-07-02 11:31

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateField(default=datetime.date.today, verbose_name='Creation date')),
                ('modification_date', models.DateField(default=datetime.date.today, verbose_name='Modification date')),
                ('email', models.EmailField(blank=True, default=None, max_length=254, null=True, verbose_name='Email address')),
                ('affiliation', models.CharField(default=None, max_length=64, verbose_name='Primary Affliation')),
                ('funding_statement', models.TextField(blank=True, default=None, null=True, verbose_name='Statement')),
                ('aboriginal_or_torres', models.NullBooleanField(choices=[(True, 'Yes'), (False, 'No'), (None, 'Prefer not to say')], default=False, verbose_name='Aboriginal or Torres Strait Islander')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-creation_date'],
                'abstract': False,
            },
        ),
    ]