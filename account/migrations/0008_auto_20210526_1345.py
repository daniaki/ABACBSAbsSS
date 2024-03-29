# Generated by Django 2.2.20 on 2021-05-26 03:45

import abstract.validators
from django.db import migrations, models
import functools


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20180917_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scholarshipapplication',
            name='has_other_funding',
            field=models.BooleanField(blank=True, default=False, verbose_name='Do you have any other sources of funding?'),
        ),
        migrations.AlterField(
            model_name='scholarshipapplication',
            name='text',
            field=models.TextField(default=None, help_text='Please explain why you are applying for this scholarship. This field is limited to 200 words or less.', validators=[functools.partial(abstract.validators.validate_n_word_or_less, *(), **{'n': 220})], verbose_name='Reason'),
        ),
    ]
