# Generated by Django 2.0 on 2018-07-03 08:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboriginalOrTorres',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateField(default=datetime.date.today, verbose_name='Creation date')),
                ('modification_date', models.DateField(default=datetime.date.today, verbose_name='Modification date')),
                ('type', models.CharField(default=None, max_length=128, unique=True)),
            ],
            options={
                'ordering': ['-creation_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CareerStage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateField(default=datetime.date.today, verbose_name='Creation date')),
                ('modification_date', models.DateField(default=datetime.date.today, verbose_name='Modification date')),
                ('name', models.CharField(default=None, max_length=128, unique=True)),
            ],
            options={
                'ordering': ['-creation_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateField(default=datetime.date.today, verbose_name='Creation date')),
                ('modification_date', models.DateField(default=datetime.date.today, verbose_name='Modification date')),
                ('type', models.CharField(default=None, max_length=128, unique=True)),
            ],
            options={
                'ordering': ['-creation_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateField(default=datetime.date.today, verbose_name='Creation date')),
                ('modification_date', models.DateField(default=datetime.date.today, verbose_name='Modification date')),
                ('name', models.CharField(default=None, max_length=128, unique=True)),
            ],
            options={
                'ordering': ['-creation_date'],
                'abstract': False,
            },
        ),
    ]
