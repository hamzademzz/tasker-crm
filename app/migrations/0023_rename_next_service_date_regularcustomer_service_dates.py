# Generated by Django 5.1.4 on 2025-01-18 00:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_remove_regularcustomer_service_dates_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='regularcustomer',
            old_name='next_service_date',
            new_name='service_dates',
        ),
    ]
