# Generated by Django 2.0 on 2018-07-07 10:09

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('abstract', '0009_auto_20180706_1740'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('status', models.CharField(blank=True, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=24, verbose_name='Status')),
                ('rejection_comment', models.TextField(default=None, help_text='Please give a reason for rejecting this review assignment.', null=True, verbose_name='Reason')),
                ('abstract', models.ForeignKey(blank=None, on_delete=django.db.models.deletion.CASCADE, related_name='assignments', related_query_name='assignment', to='abstract.Abstract')),
            ],
            options={
                'ordering': ('reviewer',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='abstractassignment',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='abstractassignment',
            name='abstract',
        ),
        migrations.RemoveField(
            model_name='abstractassignment',
            name='reviewer',
        ),
        migrations.AlterField(
            model_name='review',
            name='score_content',
            field=models.IntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)], verbose_name="Score based on the abstract's scientific content."),
        ),
        migrations.AlterField(
            model_name='review',
            name='score_contribution',
            field=models.IntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)], verbose_name="Score based on the author's contribution to the work."),
        ),
        migrations.AlterField(
            model_name='review',
            name='score_interest',
            field=models.IntegerField(default=None, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)], verbose_name="Score based on the ability of the abstract's contents to hold your interest."),
        ),
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(default=None, null=True, verbose_name='Review'),
        ),
        migrations.DeleteModel(
            name='AbstractAssignment',
        ),
        migrations.AddField(
            model_name='assignment',
            name='review',
            field=models.ForeignKey(blank=None, on_delete=django.db.models.deletion.CASCADE, related_name='assignments', related_query_name='assignment', to='abstract.Review'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='reviewer',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='assignments', related_query_name='assignment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together={('reviewer', 'abstract')},
        ),
    ]
