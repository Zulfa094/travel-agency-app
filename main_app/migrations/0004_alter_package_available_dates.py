# Generated by Django 5.1.5 on 2025-02-18 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_auto_20250217_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='available_dates',
            field=models.TextField(default='[]'),
        ),
    ]
