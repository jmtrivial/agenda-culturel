# Generated by Django 4.2.7 on 2023-11-15 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agenda_culturel', '0002_alter_event_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.ForeignKey(default=None, help_text='Category of the event', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='agenda_culturel.category', verbose_name='Category'),
        ),
    ]
