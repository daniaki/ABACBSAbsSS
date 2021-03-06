# Generated by Django 2.0 on 2018-08-08 08:40

import abstract.validators
from django.db import migrations, models
import functools


class Migration(migrations.Migration):

    dependencies = [
        ('abstract', '0017_auto_20180710_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstract',
            name='author_affiliations',
            field=models.TextField(blank=True, default=None, help_text='Please list the primary affiliations of all contributing authors including yourself (new line separated).', verbose_name='Contributing author affiliations'),
        ),
        migrations.AlterField(
            model_name='abstract',
            name='authors',
            field=models.TextField(blank=True, default=None, help_text='Please list all contributing authors including yourself (new line separated).', verbose_name='Contributing authors'),
        ),
        migrations.AlterField(
            model_name='abstract',
            name='categories',
            field=models.ManyToManyField(help_text='Please select one or more categories for your abstract. You must be registered for the conference and sessions that you apply to.', related_name='abstracts', related_query_name='abstract', to='abstract.PresentationCategory', verbose_name='Categories'),
        ),
        migrations.AlterField(
            model_name='abstract',
            name='contribution',
            field=models.TextField(default=None, help_text='Please describe your contribution to the research detailed in your abstract using 100 words or less.', validators=[functools.partial(abstract.validators.validate_n_word_or_less, *(), **{'n': 100})], verbose_name='Your contribution'),
        ),
        migrations.AlterField(
            model_name='abstract',
            name='keywords',
            field=models.ManyToManyField(help_text='Please assign a few keywords to your abstract. You may enter keywords that do not appear in this list by pressing Return/Enter on your keyboard.', related_name='abstracts', related_query_name='abstract', to='abstract.Keyword', verbose_name='Keywords'),
        ),
        migrations.AlterField(
            model_name='abstract',
            name='text',
            field=models.TextField(default=None, help_text='Your abstract is limited 250 words.', validators=[functools.partial(abstract.validators.validate_n_word_or_less, *(), **{'n': 250})], verbose_name='Abstract'),
        ),
    ]
