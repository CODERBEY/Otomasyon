# Generated by Django 5.0.1 on 2025-05-11 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automations', '0003_automation_config_template_automation_input_fields_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='automation',
            name='usage_guide',
            field=models.TextField(blank=True, help_text='Markdown formatinda yazabilirsiniz', verbose_name='Kullanim Kilavuzu'),
        ),
    ]
