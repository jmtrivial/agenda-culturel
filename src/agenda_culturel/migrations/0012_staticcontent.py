# Generated by Django 4.2.1 on 2023-11-09 21:35

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda_culturel', '0011_alter_event_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Category name', max_length=512, unique=True, verbose_name='Name')),
                ('text', ckeditor.fields.RichTextField(help_text='Text as shown to the visitors', verbose_name='Content')),
            ],
        ),
    ]
