# Generated by Django 5.1.4 on 2025-01-09 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='end_time',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='start_time',
            field=models.TimeField(),
        ),
    ]
