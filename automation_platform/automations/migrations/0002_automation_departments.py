# Generated by Django 5.0.1 on 2025-05-11 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automations', '0001_initial'),
        ('departments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='automation',
            name='departments',
            field=models.ManyToManyField(blank=True, related_name='automations', to='departments.department'),
        ),
    ]
