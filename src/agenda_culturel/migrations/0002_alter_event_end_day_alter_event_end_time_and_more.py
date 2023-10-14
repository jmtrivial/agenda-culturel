# Generated by Django 4.2.1 on 2023-10-14 10:04

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda_culturel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_day',
            field=models.DateField(blank=True, help_text='End day of the event, only required if different from the start day.', null=True, verbose_name='End day of the event'),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.TimeField(blank=True, help_text='Final time', null=True, verbose_name='Final time'),
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.URLField(blank=True, help_text='URL of the illustration image', null=True, verbose_name='Illustration'),
        ),
        migrations.AlterField(
            model_name='event',
            name='image_alt',
            field=models.CharField(blank=True, help_text='Alternative text used by screen readers for the image', max_length=512, null=True, verbose_name='Illustration description'),
        ),
        migrations.AlterField(
            model_name='event',
            name='reference_urls',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, help_text='List of all the urls where this event can be found.', null=True, size=None, verbose_name='URLs'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.TimeField(blank=True, help_text='Starting time', null=True, verbose_name='Starting time'),
        ),
    ]
